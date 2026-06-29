# Reflection Report

## Title
**River Crossing Puzzle Adventure: Fantasy Kingdom Escape** (Python + Pygame)

## 1. Introduction
This project is an academic implementation of a classic transportation puzzle, presented as a 2D game with a fantasy narrative. The player must help a Wizard safely transport four magical entities across a dangerous river before time runs out. The project uses **Python** and **Pygame**, and it is structured using **Object-Oriented Programming (OOP)** principles to promote maintainability, testability, and clear separation of responsibilities.

Unlike a purely text-based puzzle solver, this game emphasizes interactive gameplay elements: real-time input, smooth movement animation, a countdown timer, a pause system, a restart flow, multiple screens (menu, instructions, gameplay, pause, win, lose), and immediate feedback when rules are violated. The goal is to deliver a complete, runnable, GitHub-ready codebase that can be understood and assessed as an academic software engineering artifact.

## 2. Project Objectives
The project objectives were:

1. Build a complete 2D puzzle game in **Python + Pygame**.
2. Use OOP to design a clean architecture with clear class responsibilities.
3. Implement the puzzle constraints faithfully:
   - Only the Wizard controls transportation.
   - Boat capacity is the Wizard plus one entity.
   - Dragon and Baby Phoenix cannot be left together without the Wizard.
   - Magic Crystal and Potion Chest cannot be left together unattended.
4. Provide required game features: game loop, keyboard controls, pause, restart, countdown timer, smooth movement, sound effects, and rule validation.
5. Provide bonus features for a stronger academic deliverable: multiple levels, scoring, bilingual UI (English/Malay), and saving best score.
6. Include documentation (UML diagram and reflection report) and tests.

## 3. Requirements Analysis
### 3.1 Functional Requirements
The game must allow players to:

- Navigate a start menu.
- Read instructions.
- Play the main puzzle with a controllable boat.
- Pause/resume and restart.
- Win by transporting all entities to the right bank.
- Lose when a rule is violated or when the timer expires.

### 3.2 Non-Functional Requirements
The project must:

- Run reliably on typical student machines.
- Be readable and modular.
- Use a GitHub-ready structure.
- Avoid dependence on external binary assets (optional but beneficial for portability).

To satisfy portability, visuals are procedurally drawn (rectangles/ellipses with a modern UI style), and sounds are generated procedurally at runtime rather than requiring WAV files. The `assets/` folder remains present for compliance and for future expansion.

For the safety constraints, the phrase “unattended” is interpreted as **left alone together without the Wizard** (i.e., the problematic pair is the only pair present on that bank while the Wizard is away). This interpretation keeps the rules meaningful while ensuring the puzzle is solvable with the stated boat capacity.

## 4. OOP Architecture and Class Responsibilities
The system is intentionally decomposed into classes aligned with typical game architecture patterns:

### 4.1 GameManager
**Responsibility:** Owns the main game loop, manages game state transitions, creates levels, updates objects, and routes input events.

Key reasons for this design:
- Centralizes state flow so screens behave consistently.
- Avoids coupling the UI rendering code to gameplay state changes.
- Allows future expansion (e.g., adding more levels or new screens).

### 4.2 UIManager
**Responsibility:** Renders all screens and UI text. It also stores translation strings and provides a `t(key)` lookup function.

Why this matters:
- Keeps drawing logic separate from rules and movement.
- Makes bilingual support straightforward: translate keys rather than hard-coding text.

### 4.3 Entity and Character
**Entity** represents any movable object (Dragon, Crystal, Chest, Phoenix). It stores its position, side (left/right/boat), target position, and has an `update()` method for smooth interpolation.

**Character** extends Entity by adding the capability flag `can_control_boat`. The Wizard is represented by `Character`, while the other items are `Entity`.

This structure makes it easy to add new characters later (e.g., a guard or a knight) without rewriting the base movement and rendering system.

### 4.4 Boat
The Boat manages:
- Which side it is docked at
- Which passengers are onboard
- Whether it is currently moving
- Cross-river animation timing

Boat rules are enforced through capacity checks and a requirement that the Wizard must be onboard to cross.

### 4.5 PuzzleLogic
PuzzleLogic validates constraints independently from rendering. This separation makes it possible to test rules in isolation using automated tests.

The validation algorithm:
- Collects which entities are on each bank.
- Determines whether the Wizard is “present” on a bank (either on the bank or on a docked boat at that bank).
- If the Wizard is absent, checks for forbidden pairings.

The validator returns a `ValidationResult(ok, reason_key)` so the UI can present an appropriate message in either language.

### 4.6 Timer
Timer tracks remaining time, supports pause/resume, and converts seconds to a human-readable `MM:SS` format. The timer is updated per-frame during gameplay.

### 4.7 Level
Level is a data structure that defines difficulty tuning:
- Countdown duration
- Boat crossing speed
- Score multipliers and penalties

This enables multiple levels while reusing the same underlying puzzle entities and rules.

## 5. Gameplay Flow and Screens
The application implements a full screen/state cycle:

1. **Start Menu**: Start game, view instructions, quit.
2. **Instructions**: Rules and controls.
3. **Main Game**: Puzzle play with HUD.
4. **Pause**: Overlay with resume/restart/menu options.
5. **Win Screen**: Shows score and supports advancing to the next level.
6. **Lose Screen**: Shows the violation reason and allows retry.

This arrangement mirrors typical professional game patterns: each screen is a state, and the main loop updates and draws based on the current state.

## 6. Movement and Animation
Smooth movement was implemented using a target-position interpolation model:

- Each Entity has `pos` and `target_pos`.
- On every frame, `pos` moves toward `target_pos` using a smoothing constant.
- The Boat uses a timed easing function for crossing the river.

Passengers are attached visually to the boat while crossing by updating their positions to slot locations on the boat each frame, ensuring cohesive motion.

## 7. Scoring and Persistence
Scoring rewards quick and efficient solutions:

- **Time score** = remaining seconds × level multiplier
- **Move penalty** = number of actions × penalty
- Final score = `max(0, time score − move penalty)`

The best score is stored in `save/best_score.json`. This file is written atomically to prevent corruption.

## 8. Sound Design
Sound effects are produced procedurally as short sine-wave tones with a decay envelope. This approach avoids dependency on external WAV files while still meeting the “sound effects” requirement.

In future iterations, the procedural sounds could be replaced with themed sound assets (water splashes, magical chimes, etc.) by loading WAV files from `assets/sounds/`.

## 9. Testing Strategy
Automated tests focus on non-graphical logic:

- PuzzleLogic validation scenarios (valid states and rule violations)
- Timer countdown behavior and formatting

This reflects a common game testing approach: pure logic is unit-tested, while rendering is typically validated manually or with higher-level integration testing.

## 10. Challenges Encountered and Solutions
### 10.1 Rule Validation Timing
One subtle point is when to validate the puzzle. If validation only occurs after the boat arrives, the player could temporarily leave forbidden pairings behind and still continue. The solution was to validate immediately after each action, including when crossing begins.

### 10.2 Keeping Passengers Attached to the Boat
If passengers simply “chase” the boat target, they may lag behind the boat during fast movement. The implementation updates passenger positions while the boat is moving, ensuring they appear seated on the boat during the crossing animation.

### 10.3 Balancing Difficulty With Multiple Levels
The puzzle itself remains constant (five entities), but difficulty can be adjusted by changing the timer and crossing duration. This preserves the integrity of the required entities while still delivering meaningful multi-level progression.

## 11. Future Improvements
If more time were available, the next upgrades would be:

- Add click-to-select and drag interaction for accessibility.
- Add real sprite animations (idle bob, wing flaps) using PNG sequences.
- Add a hint system (suggest safe moves) for educational support.
- Add an achievements system for replayability.
- Add support for mobile-friendly scaling.

## 12. Conclusion
This project delivers a complete academic game implementation using Python and Pygame. It demonstrates strong OOP structure, real-time game loop architecture, UI screen management, rule validation, smooth animation, a countdown timer, audio feedback, and bonus systems such as scoring, multi-level progression, bilingual support, and best-score persistence. The codebase is intentionally modular and testable, making it suitable both for grading and for extension into a more content-rich game.

## References
- Pygame documentation: https://www.pygame.org/docs/
- Classic river crossing puzzle variants (general reference): https://en.wikipedia.org/wiki/River_crossing_puzzle
