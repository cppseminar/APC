package app

const TestAllStudentsTaskQueue = "TEST_ALL_STUDENTS_TASK_QUEUE"

type TestRequest struct {
	TaskId       string
	SubmissionId string
	TestCaseId   string
	CreatedBy    string
	TaskName     string
	TestCaseName string
	ContentUrl   string
	Counted      bool
}
