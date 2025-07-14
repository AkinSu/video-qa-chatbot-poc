import { useState } from 'react';

export default function VideoQAChatbot() {
  const [videoId, setVideoId] = useState('');
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [answer, setAnswer] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!videoId.trim() || !question.trim()) {
      setError('Please fill in both Video ID and Question fields');
      return;
    }

    setIsLoading(true);
    setError('');
    setAnswer('');

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_id: videoId.trim(),
          question: question.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnswer(data.answer || data.response || 'No answer received');
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', padding: '20px' }}>

      <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
        Hey Akin
      </h1>

      <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
        Video QA Chatbot
      </h1>
      
      {/* Add this navigation section */}
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <a 
          href="/upload" 
          style={{
            color: '#007bff',
            textDecoration: 'none',
            fontSize: '16px'
          }}
        >
          Upload New Video
        </a>
      </div>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="videoId" style={{ display: 'block', marginBottom: '5px' }}>
            Video ID:
          </label>
          <input
            id="videoId"
            type="text"
            value={videoId}
            onChange={(e) => setVideoId(e.target.value)}
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '16px'
            }}
            placeholder="Enter video ID"
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="question" style={{ display: 'block', marginBottom: '5px' }}>
            Question:
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows="4"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '16px',
              resize: 'vertical'
            }}
            placeholder="Ask a question about the video"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1
          }}
        >
          {isLoading ? 'Thinking...' : 'Ask Question'}
        </button>
      </form>

      {error && (
        <div style={{
          color: 'red',
          padding: '10px',
          border: '1px solid red',
          borderRadius: '4px',
          marginBottom: '20px',
          backgroundColor: '#fff5f5'
        }}>
          {error}
        </div>
      )}

      {answer && (
        <div style={{
          padding: '15px',
          border: '2px solid #007bff',
          borderRadius: '4px',
          backgroundColor: '#f8f9fa'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '10px' }}>Answer:</h3>
          <p style={{ margin: 0, lineHeight: '1.5' }}>{answer}</p>
        </div>
      )}
    </div>
  );
} 