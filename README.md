# Sweeping View

Sweeping view is a library that can parse replay files produced by official
Minesweeper clones, as well as Metasweeper.

It's fairly bare-bones, and doesn't do much more than parse replay files. If
you want to do actual analysis of replay files, even just getting board events
from mouse events, you probably want to use `ms-toollib` instead (see below).

## Currently supported:

Formats:
 - RMV (Viennasweeper)
 - AVF (Minesweeper Arbiter, Freesweeper)
 - EVF (Metasweeper)

Tested Python versions:
 - 3.6
 - 3.7
 - 3.8
 - 3.9
 - 3.10
 - 3.11
 - 3.12

## Is this a good idea? Shouldn't the formats be secret?

They aren't anymore anyway. There are open-source tools available to convert
the implemented formats to rawvf, an entirely text-based format.

What this library doesn't do is make any attempt to verify checksums. Those
remain as the primary obstacle to generating fake replays.

## Similar projects

### `ms-toollib`

`ms-toollib` is a library that provides way more features than `sweeping-view`.

Besides replay parsing, it also provides a fully featured minesweeper engine,
as well as numerous algorithms. It is written in Rust, but there is a Python
package of the same name on PyPI.
https://github.com/eee555/ms-toollib/

On the other hand, `sweeping-view` is pure Python and has zero dependencies -
so if all you need is metadata, it might be all you need!

### Rawvf

Rawvf is a plain-text minesweeper replay format. A collection of command line
tools to convert various formats to it can be found here:
https://github.com/thefinerminer/minesweeper-rawvf

Rawvf offers far better support (more formats/old versions of formats), but the
tools aren't usable as libraries.

## State of completion and stability

This library is still a work in progress, and parts of the public API may
change completely - this is because while all existing parsers work for now,
not much care has been taken to make them consistent.

## Example use

### Arbiter

#### code
```python
from sweeping_view.avf import AVFReplay

avf = AVFReplay.from_file("HI-SCORE Beg_5.41_3BV=28_3BVs=5.17_Tommy.avf")

print(avf.name)
print(avf.properties)
print(avf.mines)
```

#### output

```python
'Tommy'
{'level': 'beginner', 'questionmarks': False}
[(4, 1), (5, 2), (8, 2), (2, 3), (6, 3), (4, 5), (8, 5), (6, 6), (8, 6), (4, 7)]
```

### Viennasweeper

#### code
```python
from sweeping_view.rmv import RMVReplay

rmv = RMVReplay.from_file("fd60_beg_4153_NF_1600544477.rmv")

print(rmv.player_data)
print(rmv.properties)
print(rmv.mines)
```

#### output

```python
{'name': 'tkolar'}
{'questionmarks': False, 'nonflagging': True, 'mode': 'normal', 'level': 'beginner'}
[(1, 3), (2, 3), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, 4), (6, 6), (7, 6)]
```

### Metasweeper

#### code
```python
from sweeping_view.evf import EVFReplay

evf = EVFReplay.from_file("test_subject.evf")

print(evf.user_identifier)
print(rmv.bbbv)
print(rmv.timeth)
```

#### output

```python
Szymon_M
167
69597
```
