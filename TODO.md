# TODO List

## Task: Add notifications for students when FYP paper is approved and when added as co-author

### Steps:
1. [x] Analyze codebase to understand notification system
2. [x] Understand FYP paper approval flow
3. [x] Understand co-author addition flow
4. [ ] Verify FYP approval notification works for students (existing code)
5. [ ] Add co-author notification in researcher_upload_page function
6. [ ] Add co-author notification in researcher_home function

### Implementation Details:

#### 1. FYP Paper Approval Notification:
- Existing code in `submission_detail()` already sends notification to author
- Verified: Code handles both researcher and student papers correctly

#### 2. Co-author Added Notification:
Need to add notification logic in:
- `researcher_upload_page()` - after setting co-authors
- `researcher_home()` - after updating co-authors

Logic:
- For each new co-author added
- If co-author is a student (role='student')
- Create notification: "You have been added as a co-author on paper: {paper_title} by {researcher_name}"
