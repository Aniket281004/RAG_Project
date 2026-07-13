function AnswerBox({ answer }) {
  if (!answer) {
    return null;
  }

  return (
    <div className="answer-box">
      <h2>Generated Question Paper</h2>

      <pre>{answer}</pre>
    </div>
  );
}

export default AnswerBox;