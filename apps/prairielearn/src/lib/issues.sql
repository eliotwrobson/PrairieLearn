-- BLOCK insert_issue
INSERT INTO
  issues AS i (
    student_message,
    instructor_message,
    course_caused,
    course_data,
    system_data,
    authn_user_id,
    instance_question_id,
    course_id,
    course_instance_id,
    question_id,
    assessment_id,
    user_id,
    variant_id,
    manually_reported
  )
SELECT
  $student_message,
  $instructor_message,
  $course_caused,
  $course_data::jsonb,
  $system_data::jsonb,
  $authn_user_id,
  v.instance_question_id,
  v.course_id,
  v.course_instance_id,
  v.question_id,
  ai.assessment_id,
  $user_id,
  $variant_id,
  $manually_reported
FROM
  variants AS v
  LEFT JOIN instance_questions AS iq ON (iq.id = v.instance_question_id)
  LEFT JOIN assessment_instances AS ai ON (ai.id = iq.assessment_instance_id)
WHERE
  v.id = $variant_id
RETURNING
  i.id;

-- BLOCK insert_issue_if_no_open_duplicate
-- Like insert_issue, but skips insertion if an open, course-caused issue with
-- the same question, instructor_message, and student_message already exists.
-- Used for instructor-only warnings to avoid flooding the table when many
-- students trigger the same warning.
INSERT INTO
  issues AS i (
    student_message,
    instructor_message,
    course_caused,
    course_data,
    system_data,
    authn_user_id,
    instance_question_id,
    course_id,
    course_instance_id,
    question_id,
    assessment_id,
    user_id,
    variant_id,
    manually_reported
  )
SELECT
  $student_message,
  $instructor_message,
  $course_caused,
  $course_data::jsonb,
  $system_data::jsonb,
  $authn_user_id,
  v.instance_question_id,
  v.course_id,
  v.course_instance_id,
  v.question_id,
  ai.assessment_id,
  $user_id,
  $variant_id,
  $manually_reported
FROM
  variants AS v
  LEFT JOIN instance_questions AS iq ON (iq.id = v.instance_question_id)
  LEFT JOIN assessment_instances AS ai ON (ai.id = iq.assessment_instance_id)
WHERE
  v.id = $variant_id
  AND NOT EXISTS (
    SELECT
      1
    FROM
      issues AS existing
    WHERE
      existing.question_id = v.question_id
      AND existing.instructor_message IS NOT DISTINCT FROM $instructor_message
      AND existing.student_message IS NOT DISTINCT FROM $student_message
      AND existing.open = TRUE
      AND existing.course_caused = TRUE
  )
RETURNING
  i.id;
