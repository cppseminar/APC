#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <stdbool.h>
#include <signal.h>

#include <unistd.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <poll.h>

#include "support.h"

// helper function for creating all pipes
static int create_pipes_for_process(int inpipe[2], int outpipe[2], int syncpipe[2])
{
    if (pipe(inpipe) < 0)
    {
        perror("Cannot create input pipe");
        return -1;
    }

    if (pipe(outpipe) < 0)
    {
        perror("Cannot create output pipe");
        close(inpipe[0]);
        close(inpipe[1]);
        return -1;
    }

    if (pipe2(syncpipe, O_CLOEXEC) < 0)
    {
        perror("Cannot create sync pipe");
        close(inpipe[0]);
        close(inpipe[1]);
        close(outpipe[0]);
        close(outpipe[1]);
        return -1;
    }

    return 0;
}

// shorthand for closing all pipes, will check for -1 as already closed fd
// it will also set up pipe as -1 (invalid)
static int destroy_pipes_for_process(int inpipe[2], int outpipe[2], int syncpipe[2])
{
    close(inpipe[0]);
    close(inpipe[1]);
    close(outpipe[0]);
    close(outpipe[1]);
    close(syncpipe[0]);
    close(syncpipe[1]);

    return 0;
}

int process_create(const char *process_name, const char *const args[], size_t argc, process_t *result)
{
    result->status = -2; // special value for not assigned status
    
    int inpipe[2];   // stdin of new process 0 is for read, 1 is for write
    int outpipe[2];  // stdout of new process
    int syncpipe[2]; // this way child process can report exec errors

    if (create_pipes_for_process(inpipe, outpipe, syncpipe) < 0)
    {
        return -1;
    }

    result->pid = fork();
    if (result->pid < 0)
    {
        perror("Cannot fork process");
        destroy_pipes_for_process(inpipe, outpipe, syncpipe);
        return -1;
    }

    if (result->pid == 0)
    {
        // child
        close(inpipe[1]);
        close(outpipe[0]);
        close(syncpipe[0]); // other end will be closed automatically on exec

        if (dup2(inpipe[0], STDIN_FILENO) < 0)
        {
            perror("Cannot set up stdin");
            _Exit(EXIT_FAILURE);
        }
        close(inpipe[0]);

        if (dup2(outpipe[1], STDOUT_FILENO) < 0)
        {
            perror("Cannot set up stdout");
            _Exit(EXIT_FAILURE);
        }
        close(outpipe[1]);

        char *argv[argc + 2]; // dreaded VLA, if good for glibc, good for us

        // casts here are needed becasue of POSIX/C quirks
        // see remarks here
        // https://pubs.opengroup.org/onlinepubs/009604499/functions/exec.html
        argv[0] = (char *)process_name;
        for (size_t i = 0; i < argc; ++i)
        {
            argv[i + 1] = (char *)args[i];
        }
        argv[argc + 1] = NULL; // terminate

        if (execv(process_name, argv) < 0)
        {
            // we need to report error from exec to parent process
            ssize_t count = write(syncpipe[1], &errno, sizeof(errno));
            if (count < 4)
            {
                // -1 is error, <4 we cannot write whole int!
                // we are deep into it, last attempt to report something
                _Exit(52); // 52 is just arbitrary number...
            }

            close(syncpipe[1]);
            _Exit(EXIT_FAILURE);
        }

        return 0; // we will never be here, just to make gcc happy
    }
    else
    {
        // parent
        close(inpipe[0]);
        close(outpipe[1]);
        close(syncpipe[1]);

        result->read_from_child = fdopen(outpipe[0], "r");
        if (result->read_from_child == NULL)
        {
            perror("Cannot create read stream from child");
            close(inpipe[1]);
            close(outpipe[0]);
            close(syncpipe[0]);
            return -1;
        }
        result->send_to_child = fdopen(inpipe[1], "w");
        if (result->send_to_child == NULL)
        {
            perror("Cannot create write stream to child");
            fclose(result->read_from_child);
            close(inpipe[1]);
            close(syncpipe[0]);
            return -1;
        }

        // now wait for child process to exec
        int err; // we do not care about endianess - same machine
        ssize_t count = read(syncpipe[0], &err, sizeof(err));
        if (count == 0)
        {
            // this is to be expected if no error is encounter
            close(syncpipe[0]);
            return 0;
        }
        if (count == -1 && errno != EINTR)
        {
            perror("Cannot read from child sync pipe");
            fclose(result->read_from_child);
            fclose(result->send_to_child);
            close(syncpipe[0]);
            return -1;
        }
        if (count < 4)
        {
            fputs("Unable to read enough data from sync pipe", stderr);
            fclose(result->read_from_child);
            fclose(result->send_to_child);
            close(syncpipe[0]);
            return -1;
        }

        errno = err;
        perror("Error in child process during exec");
        fclose(result->read_from_child);
        fclose(result->send_to_child);
        close(syncpipe[0]);
        return -1;
    }
}

int process_send(process_t *process, const char *data, size_t size)
{
    size_t written = fwrite(data, 1, size, process->send_to_child);
    if (written != size)
    {
        perror("Error while writing data");
        return -1;
    }

    return 0;
}

int process_send_line(process_t *process, const char *line)
{
    if (fprintf(process->send_to_child, "%s\n", line) < 0)
    {
        perror("Error while writing line");
        return -1;
    }

    fflush(process->send_to_child);

    return 0;
}

char *process_read_line(process_t *process, int timeout)
{
    if (timeout >= 0)
    {
        int fd = fileno(process->read_from_child);
        if (fd < 0)
        {
            perror("Cannot retrieve FD from read stream");
            return NULL;
        }

        struct pollfd pfd = {fd, POLLIN, 0};

        int res = poll(&pfd, 1, timeout * 1000);
        if (res < 0)
        {
            perror("Poll failed");
            return NULL;
        }

        if (res == 0)
        {
            errno = ETIME;
            perror("Poll has reach timeout");
            return NULL;
        }
    }

    char *buffer = NULL;
    size_t n = 0;
    ssize_t read = getline(&buffer, &n, process->read_from_child);
    if (read < 0)
    {
        if (!feof(process->read_from_child))
        {
            // do not report end of file conditions
            perror("Cannot read line from child");
        }
        free(buffer);
        return NULL;
    }

    buffer[strcspn(buffer, "\n")] = '\0'; // chop newline

    return buffer;
}

int process_wait(process_t *process, int timeout)
{
    if (timeout < 0)
    {
        if (waitpid(process->pid, &process->status, 0) < 0)
        {
            perror("Wait for pid failed");
            return process->status = -1;
        }
        else
        {
            return WEXITSTATUS(process->status);
        }
    }
    else
    {
        for (int i = 0; i < timeout * 10 + 1; ++i)
        { // this way we do at least one
            int pid = waitpid(process->pid, &process->status, WNOHANG);
            switch (pid)
            {
            case -1:
            {
                perror("Wait for pid failed");
                return -1;
            }
            case 0:
            {
                usleep(100000);
                break;
            }
            default:
            {
                // we have succesfully waited for the process
                if (WIFSIGNALED(process->status)) {
                    fprintf(stderr, "Child process terminated %d.", process->status);
                    return EXIT_FAILURE;
                }
     
                return WEXITSTATUS(process->status);
            }
            }
        }
    }

    errno = ETIME;
    perror("Wait for process has timeouted");
    return -1; // we do not modify process->status
}

void process_close_stdin(process_t *process)
{
    FILE *tmp = process->send_to_child;
    if (tmp != NULL)
    {
        process->send_to_child = NULL;
        if (fclose(tmp) < 0)
        {
            perror("Cannot close read stream");
        }
    }
}

void process_close(process_t *process)
{
    process_close_stdin(process);
    if (fclose(process->read_from_child) < 0)
    {
        perror("Cannot close write stream");
    }
    // if process is not waited
    if (process->status == -2) {
        if (kill(process->pid, SIGKILL) < 0) {
            perror("Kill of child process failed");
            return; // here we may leak process descriptor, but better than infinite wait
        }

        process_wait(process, -1); // if kill is OK this should return immediatelly
    }
}

char* create_tmp_file(const char* data, size_t length, enum tmp_file_mode mode) {
    const char* tmp_dir = getenv("TMPDIR");
    if (tmp_dir == NULL) {
        tmp_dir = "/tmp";
    }

    const char file_tmpl[] = "test-XXXXXX";

    char* file = malloc(strlen(tmp_dir) + strlen(file_tmpl) + 2); // +1 for / and +1 for nul
    if (file == NULL) {
        perror("Cannot alocate memory for temp file name");
        return NULL;
    }

    file = strcat(strcat(strcpy(file, tmp_dir), "/"), file_tmpl);

    int fd = mkstemp(file);
    if (fd < 0) {
        perror("Cannot create temporary file...");
        free(file);
        return NULL;
    }

    size_t off = 0;
    while (off < length) {
        ssize_t count = write(fd, data + off, length - off);
        if (count < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("Cannot write to temp file");
            free(file);
            close(fd);
            return NULL;
        }

        off += count;
    }
    
    close(fd);

    switch (mode)
    {
    case TFM_RO:
        if (chmod(file, S_IRUSR | S_IRGRP | S_IROTH) < 0) {
            perror("Cannot set readonly to file");
            free(file);
            return NULL;
        }
        break;

    case TFM_WO:
        if (chmod(file, S_IWUSR | S_IWGRP | S_IWOTH) < 0) {
            perror("Cannot set writeonly to file");
            free(file);
            return NULL;
        }
        break;
    
    case TFM_RW:
    default:
        break;
    }

    return file;
}

bool remove_file(const char* path) {
    if (unlink(path) < 0) {
        perror("Cannot unlink file");
        return false;
    }

    if (access(path, F_OK) == 0) {
        perror("File still exists");
        return false;
    }

    return true;
}