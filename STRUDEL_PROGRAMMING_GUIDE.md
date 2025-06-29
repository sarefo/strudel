# Strudel Programming Guide

A comprehensive reference for programming music with Strudel live coding language.

## Overview

Strudel is a JavaScript-based live coding music environment that ports the TidalCycles pattern language to the browser. It allows expressive creation of dynamic music pieces through algorithmic patterns and real-time manipulation.

### Key Concepts
- **Patterns**: The core building blocks - everything in Strudel is a pattern
- **Cycles**: Time is divided into repeating cycles, patterns play within these cycles
- **Functions**: Pure functions that create and transform patterns
- **Mini Notation**: Compact syntax for expressing rhythmic patterns
- **Live Coding**: Real-time pattern modification while music plays

## Mini Notation Syntax

Mini notation provides a compact way to express patterns using a domain-specific language.

### Basic Elements

#### Sequence
```strudel
note("c e g b")           // Play notes in sequence
s("bd hh sd hh")          // Drum sequence
```

#### Rests and Silence
```strudel
note("c ~ e ~")           // Use ~ for silence/rests
s("bd ~ sd ~")            // Classic drum pattern with rests
```

#### Sample Selection
```strudel
s("casio:0 casio:1 casio:2")  // Select different samples from set
s("drum:0 drum:1 drum:2")     // Computer counts from 0
```

### Time Manipulation

#### Multiplication (Speed Up)
```strudel
note("[c e g b]*2")       // Play sequence twice as fast
s("bd*4")                 // Repeat bd 4 times per cycle
note("[e5 b4 d5 c5]*2.75") // Use decimal values
```

#### Division (Slow Down)
```strudel
note("[c e g b]/2")       // Play sequence over 2 cycles
s("bd/4")                 // Play bd every 4 cycles
```

#### Angle Brackets (Sequence Over Multiple Cycles)
```strudel
note("<c e g b>")         // Each note lasts one full cycle
s("<bd hh sd>")           // Cycle through drum sounds
```

### Subdivisions and Nesting

#### Square Brackets (Subdivisions)
```strudel
note("c [e g] b")         // [e g] subdivides the second beat
s("bd [hh hh] sd hh")     // Create hi-hat subdivisions
note("[b4 [~ c5] d5 e5]") // Nested subdivisions with rests
```

#### Parallel Events (Chords)
```strudel
note("[c,e,g]")           // Play chord simultaneously
s("[bd,hh]")              // Layer kick and hi-hat
note("[g3,b3,e4]")        // Three-note chord
```

### Advanced Patterns

#### Euclidean Rhythms
```strudel
s("bd(3,8)")              // 3 beats distributed over 8 steps
s("hh(5,8)")              // 5 hi-hats over 8 steps
s("bd(3,8,2)")            // With offset of 2
```

#### Elongation (@)
```strudel
note("<[g3,b3,e4]@2 [a3,c3,e4]>")  // First chord lasts twice as long
s("bd@3 hh sd")                     // Kick gets 3x weight
```

#### Replication (!)
```strudel
note("c!4")               // Repeat c 4 times (same as c c c c)
s("<bd!2 sd>")            // Repeat without speeding up
```

#### Randomness
```strudel
s("bd? hh sd?")           // ? = 50% probability
s("bd*4?")                // Random kick drum fills
```

#### Alternation
```strudel
s("bd <hh sd>")           // Alternate between hh and sd
note("c <e g>")           // Alternate between chord variations
```

## Pattern Functions & API

### Core Pattern Creation

#### sequence() / seq()
```strudel
sequence("c", "e", "g", "b")      // Create sequence from arguments
seq("c", "e", "g", "b")           // Short form
```

#### stack()
```strudel
stack(
  note("c e g"),
  note("c, e, g").delay(0.1)
)                                  // Layer multiple patterns
```

#### cat()
```strudel
cat(
  note("c e"),
  note("g b")
)                                  // Concatenate patterns
```

### Pattern Manipulation

#### Timing Functions
```strudel
note("c e g b").fast(2)           // Double speed
note("c e g b").slow(2)           // Half speed
note("c e g b").early(0.1)        // Shift earlier
note("c e g b").late(0.1)         // Shift later
```

#### Repetition and Variation
```strudel
note("c e g").repeat(3)           // Repeat pattern
note("c e g").palindrome()        // Play forward then backward
note("c e g").rev()               // Reverse pattern
note("c e g").iter(4)             // Rotate pattern over 4 cycles
```

#### Conditional Application
```strudel
note("c e g b").sometimes(x => x.fast(2))     // Sometimes apply function
note("c e g b").rarely(x => x.rev())          // Rarely apply function
note("c e g b").often(x => x.add(12))         // Often apply function
```

#### Random Functions
```strudel
note("c e g b").shuffle()         // Randomize order each cycle
note("c e g b").scramble(2)       // Randomize in groups of 2
choose("c", "e", "g", "b")        // Random choice
rand.range(60, 72)                // Random number in range
```

### Scale and Pitch Functions

#### Scales
```strudel
note("0 2 4 6").scale("C major")  // Map to major scale
note("0 1 2 3").scale("C:minor")  // Minor scale
n("0 2 4 6").scale("C4:pentatonic") // Pentatonic scale
```

#### Chord Functions
```strudel
note("C Em F G").dict()           // Use chord dictionary
note("c e g").voicing()           // Apply voicing
chord("<C^7 Dm7 G7 C^7>")         // Jazz chord progression
```

#### Pitch Manipulation
```strudel
note("c e g").add(12)             // Transpose up octave
note("c e g").sub(7)              // Transpose down
note("c e g").mul(2)              // Frequency doubling
```

## Effects & Audio Processing

### Basic Effects
```strudel
s("bd hh sd hh").gain(0.8)        // Volume control
s("bd hh sd hh").pan(0.5)         // Stereo panning (-1 to 1)
s("bd hh sd hh").speed(1.2)       // Playback speed
```

### Time-based Effects
```strudel
s("bd hh sd hh").delay(0.25)      // Delay effect
s("bd hh sd hh").echo(4, 0.1, 0.7) // Echo (times, feedback, mix)
s("bd hh sd hh").room(0.5)        // Reverb
s("bd hh sd hh").size(0.8)        // Reverb size
```

### Filter Effects
```strudel
s("bd hh sd hh").cutoff(800)      // Low-pass filter
s("bd hh sd hh").resonance(5)     // Filter resonance
s("bd hh sd hh").hcutoff(200)     // High-pass filter
s("bd hh sd hh").bandf(1000)      // Band-pass filter
```

### Modulation Effects
```strudel
s("bd hh sd hh").crush(4)         // Bit crushing
s("bd hh sd hh").shape(0.5)       // Distortion/waveshaping
s("bd hh sd hh").vowel("a e i o") // Vowel filter
```

### Advanced Effects
```strudel
s("bd hh sd hh").begin(0.1)       // Start sample at position
s("bd hh sd hh").end(0.9)         // End sample at position
s("bd hh sd hh").loop(2)          // Loop sample n times
s("bd hh sd hh").chop(8)          // Chop into pieces
```

## Real-World Examples

### Basic Beat
```strudel
stack(
  s("bd ~ bd ~"),
  s("~ sd ~ sd"),
  s("hh*8").gain(0.3)
)
```

### Melodic Pattern
```strudel
stack(
  note("c4 eb4 f4 g4").scale("C:minor").slow(2),
  note("c3 c3 g3 c3").slow(4)
).lpf(sine.range(400, 2000).slow(8))
```

### Complex Polyrhythm
```strudel
stack(
  s("bd(3,8)"),
  s("hh(5,8)").gain(0.4),
  s("~ sd(2,8,2)"),
  note("c2 eb2 f2").slow(4).sometimes(x => x.add(12))
)
```

### Ambient Texture
```strudel
stack(
  note("c d e f g a b").scale("C:minor")
    .slow(16).echo(4, 0.125, 0.6).room(0.8),
  s("~ ~ ~ rim").delay(0.25).room(0.5).gain(0.3),
  sine.range(60, 65).slow(8) // Low drone
)
```

### Breakbeat Style
```strudel
stack(
  s("bd [~ bd] ~ bd ~ [~ bd] ~"),
  s("~ sd ~ [sd ~] ~ sd ~ sd"),
  s("hh*16").struct("1 0 1 1 1 0 1 1").gain(0.3),
  s("breaks165:0").chop(16).sometimes(x => x.rev())
).fast(1.3)
```

## Advanced Techniques

### Layer Management
```strudel
const drums = stack(
  s("bd ~ bd ~"),
  s("~ sd ~ sd")
);

const melody = note("c e g b").scale("C:major");

stack(drums, melody.delay(0.1))
```

### Pattern Sequencing
```strudel
const patterns = [
  s("bd hh sd hh"),
  s("bd*2 ~ sd ~"),
  s("bd ~ [sd sd] ~")
];

seq(...patterns).slow(4)  // Switch pattern every 4 cycles
```

### Dynamic Effects
```strudel
s("bd hh sd hh")
  .cutoff(sine.range(200, 2000).slow(4))   // Moving filter
  .gain(cosine.range(0.5, 1).fast(8))     // Tremolo effect
  .pan(tri.range(-1, 1).slow(6))          // Auto-pan
```

### Conditional Pattern Changes
```strudel
note("c e g b")
  .sometimesBy(0.25, x => x.fast(2))       // 25% chance to double speed
  .sometimesBy(0.1, x => x.add(12))        // 10% chance octave up
  .every(4, x => x.rev())                  // Reverse every 4th cycle
```

## Quick Reference

### Common Mini Notation Patterns
- `"bd ~ sd ~"` - Basic kick/snare beat
- `"hh*8"` - 8th note hi-hats
- `"[bd bd] ~ sd ~"` - Kick drum variations
- `"c [e g] b"` - Melodic subdivisions
- `"bd(3,8)"` - Euclidean rhythm
- `"bd? hh sd?"` - Random events

### Essential Functions
- `.fast(n)` / `.slow(n)` - Speed control
- `.sometimes()` / `.rarely()` / `.often()` - Probability
- `.add(n)` / `.sub(n)` - Pitch shifting
- `.gain(n)` - Volume (0-1+)
- `.pan(n)` - Stereo position (-1 to 1)
- `.delay(n)` - Echo effect
- `.room(n)` - Reverb (0-1)
- `.cutoff(n)` - Low-pass filter

### Scales and Chords
- `.scale("C:major")` - Major scale
- `.scale("C:minor")` - Minor scale  
- `.scale("C:pentatonic")` - Pentatonic
- `chord("C Em F G")` - Chord progressions

### Pattern Combinators
- `stack()` - Layer patterns
- `cat()` - Concatenate patterns
- `seq()` - Sequence from arguments
- `choose()` - Random selection

This guide covers the essential concepts and syntax for programming music with Strudel. The language is designed to be learned incrementally - start with simple patterns and gradually incorporate more advanced techniques as you become comfortable with the basics.