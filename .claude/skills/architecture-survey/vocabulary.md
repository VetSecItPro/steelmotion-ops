# /architecture-survey - vocabulary and tests

Use these words exactly in the report and the hand-off. Consistent words are the point: a report
that says "component" in one card and "service" in the next makes the operator translate.

## Terms

**Module**: anything with an interface and an implementation, at any scale: a function, a file, a
package, a slice that crosses layers. _Avoid_: unit, component, service.

**Interface**: everything a caller must know to use the module correctly. Not only the type
signature: also ordering constraints, invariants, error modes, required setup, performance
characteristics. _Avoid_: API, signature (both too narrow).

**Implementation**: the code inside a module.

**Depth**: how much behavior a caller or a test reaches per unit of interface it has to learn.
**Deep**: much behavior behind a small interface. **Shallow**: an interface nearly as complex as
what it hides. Depth is a property of the interface, not of the line count.

**Seam** (Michael Feathers): the place where behavior can be changed without editing at that place;
where a module's interface lives. Where to put the seam is its own decision. _Avoid_: boundary.

**Adapter**: a concrete thing that fills an interface at a seam (the real Chrome link, a fake one in
tests). Describes the role, not the contents.

**Leverage**: what callers get from depth: more capability per thing learned.

**Locality**: what maintainers get from depth: a change, a bug, a fact lives in one place instead of
spreading across callers.

## The tests

**Deletion test.** Imagine deleting the module and inlining what it does into its callers.
- Complexity vanishes: it was a pass-through. Shallow; a candidate for merging away.
- Complexity reappears in N callers: it was earning its keep. Leave it, or deepen it further.
- A module that does not exist yet (one rule restated in N files): ask the reverse. If the rule
  were written once, what would move out of the N files, and would their own code get simpler?

**The interface is the test surface.** Callers and tests should cross the same seam. A test that has
to reach past the interface (private state, the database behind a repository, a real browser for a
logic question) says the module is the wrong shape.

**One adapter means a hypothetical seam; two means a real one.** Do not propose a seam where nothing
varies across it. The second adapter is often the test fake: if the only way to test a piece of
logic is the real dependency, that is the case for a seam.

## Friction signals to look for

- Understanding one concept means bouncing between many small modules (low locality).
- A module's interface is nearly as large as its body (shallow).
- Pure functions extracted for testability while the bugs live in how they are called.
- Mutable state shared across many inner functions, guarded by comments about ordering.
- The same condition re-checked in several places because the state could change between them.
- A dependency pointing the wrong way (a lower layer importing from a higher one).
- Logic that can only be tested end to end, so its tests are slow, serial or flaky.

## Not friction (report under "leave alone")

- A long module that is pure, declarative and well tested.
- Code that is complex because the problem is complex, with a WHY comment.
- Duplication between things that look alike but model different concepts.
- Anything a decision record chose deliberately, unless the friction since is real and cited.
