"use client";

export function QuestionSelect({ question, options }: { question: string; options: string[] }) {
  return (
    <form method="get">
      <input type="hidden" name="tab" value="compare" />
      <label htmlFor="question">Select a question:</label>
      <select
        id="question"
        name="question"
        defaultValue={question}
        onChange={(event) => event.currentTarget.form?.requestSubmit()}
      >
        {options.map((option) => (
          <option key={option} value={option}>{option}</option>
        ))}
      </select>
      <button type="submit">Show</button>
    </form>
  );
}
