// Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
// Systems

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_THREADS 32768

void *f(void *arg) {
  long period_in_sec = (long) arg;
  long long end_time = period_in_sec + time(NULL);

  // Busy wait.
  while (time(NULL) < end_time);

  pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
  pthread_t tid[MAX_THREADS];

  // Parse command-line arguments.
  if (argc != 5) {
    printf("Usage: cpuinterference [min_threads] [max_threads] [thread_step] [period_in_sec]\n");
    exit(1);
  }
  int min_threads = atoi(argv[1]);
  int max_threads = atoi(argv[2]);
  int thread_step = atoi(argv[3]);
  int period_in_sec = atoi(argv[4]);
  printf("Starting CPU interference program with parameters:\n");
  printf("    min_threads = %d\n", min_threads);
  printf("    max_threads = %d\n", max_threads);
  printf("    thread_step = %d\n", thread_step);
  printf("    period_in_sec = %d\n", period_in_sec);

  while (1) {
    // Initially, spawn `min_threads` threads to be executed for `period_in_sec` seconds.
    // At each iteration, spawn `thread_step` more threads.
    // Finally, stop when `max_threads` threads is reached.
    for (int n_threads = min_threads; n_threads <= max_threads; n_threads += thread_step) {
      // Spawn `n_threads` threads executing function `f`.
      for (int thread_it = 0; thread_it < n_threads; thread_it++)
        pthread_create(&tid[thread_it], NULL, f, (void *) (long) period_in_sec);
      // Join threads.
      for (int thread_it = 0; thread_it < n_threads; thread_it++)
        pthread_join(tid[thread_it], NULL);
    }
  }

  return 0;
}