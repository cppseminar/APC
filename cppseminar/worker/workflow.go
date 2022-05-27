package app

import (
	"log"
	"time"

	"go.temporal.io/api/enums/v1"
	"go.temporal.io/sdk/workflow"
)

// return user if test cannot be run, otherwise empty string
// at this point Counted, CreatedBy, TaskId and TestCaseId from request is filled in
func RunNewestSubmissionForUser(ctx workflow.Context, request TestRequest, user string) error {
	options := workflow.ActivityOptions{
		StartToCloseTimeout: time.Second * 10,
	}
	ctx = workflow.WithActivityOptions(ctx, options)

	var submissionId string
	err := workflow.ExecuteActivity(ctx, GetNewestSubmissionIdForTask, user, request.TaskId).Get(ctx, &submissionId)
	if err != nil {
		log.Println("Cannot get newest submission id", err)
		return err
	}
	request.SubmissionId = submissionId

	var submission Submission
	err = workflow.ExecuteActivity(ctx, GetSubmission, user, submissionId).Get(ctx, &submission)
	if err != nil {
		log.Println("Cannot get content of submission", err)
		return err
	}
	request.ContentUrl = submission.Content
	request.TaskName = submission.TaskName

	err = workflow.ExecuteActivity(ctx, RunTest, request).Get(ctx, nil)
	if err != nil {
		log.Println("Cannot run test", err)
		return err
	}

	return nil
}

// returns list of user that do have submitted solution, but something bad happend there
// at this point Counted, CreatedBy and TestCaseId from request is filled in
func TestAllStudentsWorkflow(ctx workflow.Context, request TestRequest) ([]string, error) {
	options := workflow.ActivityOptions{
		StartToCloseTimeout: time.Second * 10,
	}
	ctx = workflow.WithActivityOptions(ctx, options)

	testCaseFut := workflow.ExecuteActivity(ctx, GetTestCase, request.TestCaseId)

	studentsFut := workflow.ExecuteActivity(ctx, GetAllUsers)

	var testCase TestCase
	if err := testCaseFut.Get(ctx, &testCase); err != nil {
		return nil, err
	}
	request.TaskId = testCase.TaskId
	request.TestCaseName = testCase.Name

	var students []string
	if err := studentsFut.Get(ctx, &students); err != nil {
		return nil, err
	}

	childWorkflowOptions := workflow.ChildWorkflowOptions{
		ParentClosePolicy:        enums.PARENT_CLOSE_POLICY_TERMINATE,
		WorkflowExecutionTimeout: time.Minute,
	}
	ctx = workflow.WithChildOptions(ctx, childWorkflowOptions)

	var futures []workflow.Future
	for _, student := range students {
		fut := workflow.ExecuteChildWorkflow(ctx, RunNewestSubmissionForUser, request, student)
		futures = append(futures, fut)
	}

	var results []string
	for i, fut := range futures {
		if err := fut.Get(ctx, nil); err != nil {
			log.Println("Cannot wait for future", err)
			results = append(results, students[i])
		}
	}

	return results, nil
}