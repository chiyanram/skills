Do not add @Retry: it hides the race and lets a real failure pass on a later try. Fix the wait instead.
