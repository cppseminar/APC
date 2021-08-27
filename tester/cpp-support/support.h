#ifndef SUPPORT_H_INCLUDED__
#define SUPPORT_H_INCLUDED__

#include <stdio.h>
#include <stdlib.h>

typedef struct process_t
{
    FILE *send_to_child;
    FILE *read_from_child;
    pid_t pid;
    int status;
} process_t;

int process_create(const char *process_name, const char *const args[], size_t argc, process_t *result);

int process_send(process_t *process, const char *data, size_t size);

int process_send_line(process_t *process, const char *line);

// output should be freed
// timeout is in seconds, -1 for infinite
// when timeout occurred return value is NULL and errno is set to ETIME
char *process_read_line(process_t *process, int timeout);

// will return -1 on error, process return value in success
// if timeout occur errno is se to ETIME
// timeout -1 is wait forever, otherwise in seconds
int process_wait(process_t *process, int timeout);

void process_close_stdin(process_t *process);

void process_close(process_t *process);

enum tmp_file_mode {
    TFM_RW, 
    TFM_RO, 
    TFM_WO,
};

// outputs the file name, should be freed with free
char* create_tmp_file(const char* data, size_t length, enum tmp_file_mode mode);

bool remove_file(const char* path);

#endif
