@echo off

REM Wait until specified time
REM
REM Wait for next day if actual time > 12:00 and specified time <12:00
REM
REM USAGE: wait-until 09:30
REM
REM Time must have two hour digits hh:mm with leading 0 if required.

echo on

@REM If specified time is in the evening, we don't need to wait for next day
IF %1 GTR 12:00 GOTO same_day
  @REM Target time is in the morning
  @REM Wait until time is also morning. (ie wait for next day if actual time > 12:00 and specified time <12:00)
  :not_morning
  timeout 2 > nul
  IF %TIME: =0% GTR 12:00 GOTO not_morning
:same_day

:loop
timeout 2 > nul
IF %TIME: =0% LSS %1 GOTO loop

@echo off

REM %TIME% has a leading space instead of a leading zero before 10:00 (e.g.  9:30).
REM This will result in comparisons like "if  9:30 LSS 10:00" which will be false because 9 > 1.
REM A simple workaround for this is to use %TIME: =0% to replace the space with a zero.

REM Without any delays, the loop may consume a lot of CPU.
REM So we can use timeout to sleep for a few seconds between checks.

REM Because it uses string comparison, you can omit trailing 0 values from your time.
REM For example, 09:30:00.00 can be reduced to 09:30 (or even 09:3).
