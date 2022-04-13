// Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
// Systems

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#define MAX_THREADS 32768

void *f(void *arg) {
  long duration_in_ms = (long) arg;
  clock_t start_time = clock();

  // Busy wait.
  while ((clock() - start_time) / (CLOCKS_PER_SEC / 1000.0) < duration_in_ms);

  pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
  pthread_t tid[MAX_THREADS];

  // Parse command-line arguments.
  if (argc != 6) {
    printf("Usage: cpuinterference [min_threads] [max_threads] [thread_step] [period_in_sec] [duration_in_ms]\n");
    exit(1);
  }
  int min_threads = atoi(argv[1]);
  int max_threads = atoi(argv[2]);
  int thread_step = atoi(argv[3]);
  int period_in_sec = atoi(argv[4]);
  int duration_in_ms = atoi(argv[5]);
  printf("Starting CPU interference program with parameters:\n");
  printf("    min_threads = %d\n", min_threads);
  printf("    max_threads = %d\n", max_threads);
  printf("    thread_step = %d\n", thread_step);
  printf("    period_in_sec = %d\n", period_in_sec);
  printf("    duration_in_ms = %d\n", duration_in_ms);

  while (1) {
    for (int n_threads = min_threads; n_threads <= max_threads; n_threads += thread_step) {
      // Wait period.
      clock_t start_time = clock();
      while ((clock() - start_time) / CLOCKS_PER_SEC < period_in_sec)
        sleep(1);
      // Spawn `n_threads` threads executing function `f`.
      for (int thread_it = 0; thread_it < n_threads; thread_it++)
        pthread_create(&tid[thread_it], NULL, f, (void *) (long) duration_in_ms);
      // Join threads.
      for (int thread_it = 0; thread_it < n_threads; thread_it++)
        pthread_join(tid[thread_it], NULL);
    }
  }

  return 0;
}