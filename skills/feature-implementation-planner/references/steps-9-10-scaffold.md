## Step 9 — Scaffold only (after approval, no business logic)

The scaffold creates the **shape** of the feature, with no behavior yet. This lets the user review structure, names, and wiring in real code before any logic exists, and it gives TDD a ready place to start: the tests exist and fail, and the next step is making them pass one by one.

### What the scaffold includes
Create exactly the files listed in "Files affected" (Step 4.1), and nothing else:

| Part | Include | Leave out (TODO) |
|---|---|---|
| Migration file | The file with the DDL from Step 3.3, named per convention | **Do not run it.** No DB writes |
| Entities / models | New fields, column mappings, relationships, the `version` field | Domain methods with rules |
| DTOs | All fields, types, and declarative validation (`@NotBlank`, `@Size`, `@Pattern`), with each field's meaning from Step 4.3 as a doc comment | Mapping logic |
| Error codes | New enum entries / constants | — |
| Controller / routes | Endpoint mappings, HTTP method, path, auth principal parameter, `@Valid`, security annotations from Step 5 (e.g. `@RateLimited`), delegation to the service | Any `if`, calculation, or query |
| Service / handler | Public method signatures; constructor-injected dependencies | Method bodies: throw a not-implemented error |
| Repository | Interface method signatures (e.g. `findByPublicIdAndCustomerId`) | Custom query bodies |
| Validator / helpers | Class + method signatures | Rule logic |
| Tests | Every test class and every test method from Step 7, named exactly as planned, in the same group order | Arrange/act/assert code |

### Rules
- **No business logic.** No conditionals, calculations, queries, ownership checks, or mapping. Every method body that would hold logic throws the language's not-implemented error, and has a TODO that states the intent in plain words, with no plan, AC, or ticket references (the code ships to production, the plan doesn't; see "No plan or ticket references in code" in SKILL.md):
  `// TODO: reject an expired coupon — 422 COUPON_EXPIRED, order unchanged`
  Use the plain `TODO:` tag so `grep -rn "TODO:"` lists all the remaining work; the link from each TODO to its AC / SEC / test group goes in the scaffold report's TODO map, not in the code.
- **Not-implemented errors**, by language: Java/Kotlin `throw new UnsupportedOperationException("TODO: ...")`, C# `throw new NotImplementedException()`, TypeScript `throw new Error("Not implemented: ...")`, Python `raise NotImplementedError("...")`, Go `panic("not implemented: ...")`.
- **Tests are Red on purpose.** Each test method body contains the planned Given / When / Then and Demonstrates as comments (behavior only, no group or AC numbers), and then fails explicitly: `fail("TODO: not implemented")`, `assert False`, `expect.fail(...)`, or `t.Fatal(...)`. Don't skip or disable them, because skipped tests look green and hide missing work. Keep the shared baseline setup as a TODO in the group's setup method.
- **Follow the Step 2 patterns exactly**: same folders, naming, annotations, dependency injection style, and error types.
- **It must compile/build.** Run the project's compile or type-check (`mvn -q compile test-compile`, `tsc --noEmit`, `go build ./...`, `dotnet build`, `python -m compileall`). If it doesn't compile, fix the scaffold, not by adding logic. Running the test suite is fine: every new test should fail, and every existing test should still pass.
- **Still not allowed:** running migrations, writing to any database, installing new dependencies (if one is needed, ask first), `git commit`/`push`, or editing files outside the "Files affected" list. If a file not on the list must change for the build to compile, stop and ask.

### Scaffold report
Write it to its own file next to the plan, `<ID>-scaffold-report.md` (e.g. `docs/features/plans/US-5-scaffold-report.md`), starting with `# Scaffold Report: [Feature name]` and a line `Status: … · Plan: [link to plan file] · Date: YYYY-MM-DD`, then `## 9. Scaffold report`. In the plan file, add a short `## 9–10. Scaffold report & verification` section that links to it. Neither file is listed in "Files affected" or counts as an extra file. The report contains:
1. **File tree** of created (🆕) and modified (✏️) files.
2. **Build result** (compile command + pass/fail) and **test result** (expected: N new failing tests, 0 broken existing tests).
3. **TODO map**: a table of each TODO → file:line → AC / SEC / test group it belongs to.
4. **Suggested first test** to make green (the simplest baseline ✅ from Group 1).

Then go straight to Step 10 in the same response.

## Step 10 — Verification checkpoint (STOP before logic)

This is a hard gate. The scaffold is the last moment when changing names, endpoints, DTO fields, or the schema is cheap. Once logic and tests are filled in, every structural change costs rework. So the agent checks its own work first, then hands the user a short checklist and **stops**.

### 10a. Self-verification (agent runs this, read-only)
Compare the scaffold against the approved plan, and report each check as ✅ or ❌:

| # | Check | How |
|---|---|---|
| V1 | Every file in "Files affected" exists, and no extra files were created or modified (the plan file and the scaffold report file are the only allowed extras) | `git status` / `git diff --stat` vs Step 4.1 list |
| V2 | Endpoints match Step 4.2 (method, path, status codes) | read the controller/routes |
| V3 | DTO fields match Step 4.3 (names, types, required, validation) | read the DTOs |
| V4 | Migration DDL matches Step 3.3, and it was **not** executed | read the file; no DB writes happened |
| V5 | Security wiring from Step 5 is present (auth principal, rate limit annotation, etc.) | read the controller/config |
| V6 | Every planned test exists, with the exact name, and the count matches Step 7 | list test methods vs plan; report "planned N / found N" |
| V7b | **No plan references in code**: no AC/SEC/group numbers, ticket ids, `§` sections, or `docs/` paths in any added line | the grep in SKILL.md "No plan or ticket references in code" |
| V7 | **No logic leaked**: new method bodies only contain TODOs + not-implemented errors; no conditionals, queries, or calculations | `git diff` review of new method bodies |
| V8 | Build passes; new tests fail; existing tests still pass | the command outputs from Step 9 |

If any check is ❌, fix the scaffold (never by adding logic) and re-run the checks before showing the user.

### 10b. Ask the user to verify
Append the self-verification table and the checklist below to the scaffold report file as `## 10. Verification`, and update the status line in both files. In chat, give the link to the scaffold report, the V1–V8 (incl. V7b) pass/fail summary, and the checklist. These are things only a human can judge:

```
Please verify before I implement any logic:
☐ File locations and class/method names look right for our codebase
☐ Endpoint URLs, HTTP methods, and status codes are what you want
☐ DTO fields (names, types, required) are final — the API contract is about to be locked in
☐ Migration DDL is correct (column types, nullability, FK rule, index)
☐ The test list is complete — any missing negative or security case?
☐ TODO map covers all the work

Reply "verified" to start implementing logic test-by-test,
or tell me what to change in the scaffold.
```

### 10c. Stop and wait
- End the response here. **Do not write any logic in this response**, even if everything passed.
- If the user asks for changes, apply only scaffold-level changes, re-run 10a, show the updated results, and ask again. Repeat until they reply with an explicit "verified" / "approved" / "go ahead".
- Silence, "looks ok?", or questions are not verification. Answer them, then ask again.
- Only after explicit verification may logic implementation start, one test at a time (Red → Green → Refactor), beginning with the suggested first test.
