#ifndef SUPPORT_H_INCLUDED__
#define SUPPORT_H_INCLUDED__

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

struct buffer_t {
    char* buffer;
    size_t size;
    size_t capacity;
};

bool buffer_allocate(struct buffer_t* buf, size_t size);

bool buffer_append(struct buffer_t* buf, char* data, size_t size);

// -2 allocation error
// -1 delim not there
// 0 success
int buffer_extract_delim(struct buffer_t* buf, char delim, char** output);

bool buffer_empty(struct buffer_t* buf);

typedef struct process_t
{
    int send_to_child;
    int read_from_child;
    pid_t pid;
    int status;
    struct buffer_t stdout_buffer;
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
