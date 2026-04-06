# Hello planning

## Overview

This program can make a planning based combining objects with various constraints. In a abstract way a planning has:

- a start date and time
- a end date and time. This is always after the the start date
- a combination of things that are needed. For example a person, location, a tool, a work instruction, etc.
- Some things have constraints. A certain task can only be done at a certain location for example. This is a must have rule.
- Some other aspects are optional and desirable but not must haves.
- A given planning can have a certain score on how well it implements the different desirable goals.

The goal of the program to find a planning that meets all the must have rules and has a as high as possible score on the desirable goal. The program should be abstract and possible to use in different area's.

The desirable goals, constraints and must have rules should be easy to configure or customize while the main program remains unchanged.

## Existing software

Found the following open source software:

- Optaplanner
- Timefold (Optaplanner fork)
- OR-Tools
- OptaPy (Optaplanner with python support)
- DecisionRules.io (Saas)
- 