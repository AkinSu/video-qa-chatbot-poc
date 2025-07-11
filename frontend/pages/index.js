import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file.');
      return;
    }
    if (!file.name.endsWith('.mp4')) {
      setMessage('Only MP4 files are allowed.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post(
        process.env.NEXT_PUBLIC_BACKEND_URL + '/upload',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setMessage(res.data.message);
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Upload failed.');
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', padding: 40 }}>
      <h1>Hello Akin!</h1>
      <h1>Upload MP4 Video</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="video/mp4" onChange={handleFileChange} />
        <button type="submit" style={{ marginTop: 10 }}>Upload</button>
      </form>
      {message && <p style={{ marginTop: 20 }}>{message}</p>}
    </div>
  );
} 