const connStr = process.env.MONGO_CONN_STR

const conn = connStr ? new Mongo(connStr) : new Mongo()
const dbs = conn.getDBNames()

if (dbs.indexOf('submissionsDb') == -1) {
  const db = conn.getDB('submissionsDb')

  db.createCollection('submissions', { capped: false })
  db.submissions.createIndex({ 'SubmittedOn': 1 })
  db.submissions.createIndex({ 'UserEmail': 1, 'SubmittedOn': 1 })
  db.submissions.createIndex({ 'UserEmail': 1, 'TaskId': 1, 'SubmittedOn': 1 })

  db.createCollection('tasks', { capped: false })
  db.tasks.createIndex({ 'CreatedOn': 1})
}

if (dbs.indexOf('testsDb') == -1) {
  const db = conn.getDB('testsDb')

  db.createCollection('testCases', { capped: false })
  db.testCases.createIndex({ 'CreatedAt': 1 })
  db.testCases.createIndex({ 'TaskId': 1, 'CreatedAt': 1 })

  db.createCollection('testRuns', { capped: false })
  db.testRuns.createIndex({ 'CreatedAt': 1 })
  db.testRuns.createIndex({ 'CreatedBy': 1, 'SubmissionId': 1, 'CreatedAt': 1 })
  db.testRuns.createIndex({ 'CreatedBy': 1, 'TestCaseId': 1 })
}

if (dbs.indexOf('usersDb') == -1) {
  const db = conn.getDB('usersDb')

  db.createCollection('users', { capped: false })
  db.users.createIndex({ 'UserEmail': 1 }, { unique: true })

  // add administrators
  const admins = fs.readFileSync('/data/init/admins.txt', 'utf8')
  admins
    .trim()
    .split('\n')
    .forEach(user => {
      db.users.insertOne({
          UserEmail: user.trim(),
          Claims: {
              isAdmin: 'true',
              isStudent: 'true',
          }
      })
    })
}
