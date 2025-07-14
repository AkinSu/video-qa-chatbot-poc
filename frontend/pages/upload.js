import { useState } from 'react';

export default function VideoUpload() {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'video/mp4') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid MP4 file');
      setFile(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const videoId = file.name.replace('.mp4', '');
      setSuccess(`Video uploaded successfully! Video ID: ${videoId}`);
      setFile(null);
      // Reset file input
      e.target.reset();
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
        Video Upload
      </h1>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="file" style={{ display: 'block', marginBottom: '5px' }}>
            Select MP4 Video:
          </label>
          <input
            id="file"
            type="file"
            accept=".mp4"
            onChange={handleFileChange}
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '16px'
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !file}
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
          {isLoading ? 'Uploading...' : 'Upload Video'}
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

      {success && (
        <div style={{
          color: 'green',
          padding: '10px',
          border: '1px solid green',
          borderRadius: '4px',
          marginBottom: '20px',
          backgroundColor: '#f0fff0'
        }}>
          {success}
        </div>
      )}

      <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <a 
          href="/" 
          style={{
            color: '#007bff',
            textDecoration: 'none',
            fontSize: '16px'
          }}
        >
          ← Back to Questions
        </a>
      </div>
    </div>
  );
} 