# Notation

+ `n("")` - notates samples, eg `n("0 1 2").sound("hh")` gives hh samples 0/1/2
+ `sound("")` - can write sample folder with/without sample numbers: `sound("hh:2")`
    + seems to be same as `s("")`
+  `[0 1] [1 2 3]` and `0 1 . 1 2 3` are equivalent (rhythmic feet)

## Speed
+ `s("hh bd*3")` - two beats, bd is played three times within one beat
  + so `bd*3` is same as `[bd bd bd]`
    + `[[hi lo]*1.5]*2` is `ho lo hi lo hi lo`
+ `s("hh!3")` - plays three times in three beats
  + can also use alone to repeat previous: `mt ht !` is same as `mt ht ht`
+ `s("bd [ht lt]/2")` - plays `ht` on first round, `lt` on second
  + `s("bd ht/2")` - plays `ht`on first, nothing on second!
  + so `0 <1 2 3>` and `0 [1 2 3]/3` are equivalent
+ use `.fast()` or `.slow()` to change speed
+ `[bd sd, hh:0 hh:1 hh:2]` - will play both at the same time, same cycle length (polyrhythm)
+ `{bd sd, hh:0 hh:1 hh:2}` - will instead align the steps within! (polymeter)