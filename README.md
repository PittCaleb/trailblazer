# trailblazer
AI project to blaze a trail across a screen through obstacles and towards a goal

## Execution
```bash
python trailblazer.py
```

## Requirements
There is no requirements.txt as of now.  You will probably need the following packages:  
`pip install pygame`  
`tkinter` (???)


## Usage
Upon launch, options window will open allowing you to change AI parameters

Most options are self-documenting, more explicit documentation to come

Once simulation is initiated, close the simulation window directly to exit

Once simulation is closed, you can modify parameters and re-start sim or Quit

The Stop Simulation button is non-functional at this time.

## ToDo
* Direction
  * Change from 8 ordinal possibilties to 360 degrees
* Position
  * Calculate movement mathematically (i.e. `sin()`) rather than pure STEP increments
  * Store float position, display int
* Obstacles (currently Boxes):
  * Parse box/obstacles properly
  * Use pygame collision detection rather than if-checking coordinates
  * Change Obstacle type to JSON and parse to allow for circle, polygon, etc.
* Segmentation
  * Today:
    * Segment is defined as `generations/splits`
    * Number of moves per segment is `max_moves/splits`
    * Any time new best score is found, immediately becomes parent path
    * When segment ends, next segment starts from original start position, can now travel further in its quest for the goal
  * Future:
    * Allocate half of the segments to finding "a path" and the other half to "refining the path"
    * Finding A Path (50% of segments)
      * Segment length is `generations/splits/2`
      * Max moves per segment is `max_moves/splits`
      * All attempts during segment start from the end of the previous segment (or start)
      * When segment is complete, the best of the tries is "locked in" as the best path from the end of prev segment to start of next segment
      * Next segment will **always** start from where this one terminated
    * After Finding A Path is complete, one path is formed with the combination of the previous segments, regardless as to if a win was accomplished or not
    * Refining the path
      * Starting with a base (full) path
      * This portion of the code is divided again into `split` segments
      * AI is run successively that number of times, without modifying the parent inheritance
      * At end of each segment, new best path becomes the parent and next segment is initiated
    * May need to add new parameter to allow for differing number of generations for each segment.
      * i.e. 500k to come up with basic solution, but then run this out for 1 million more just to see if a better path can ever be found

## Notes
This is a work in progress.  I read a couple of articles on AI and decided to write this without any guidence or code examples.  All algorythms and process flow were novel to me.  If you could see how this evolved you would be amazed.  This is a teaching project, for myself.

I appreciate any and all advice, however know, just having an expert toss down "this is how it's done" defeats my end goal of learning how to do this myself.

>I know I am missing many things, I am learning as I develop this AI if you will.  Just know this before commenting or offering assistance.  I am more open to hearing advice on process than in having code handed to me in the form of Pull Requests.

## Contact
Caleb Cohen  
Caleb@Hail2Pitt.org  
https://github.com/PittCaleb  
Twitter: [@PittCaleb](https://www.twitter.com/PittCaleb)


  