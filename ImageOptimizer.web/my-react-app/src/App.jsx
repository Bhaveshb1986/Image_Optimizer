/**
 * Image Optimizer – main React app component.
 *
 * Provides the UI for uploading an image, setting JPEG quality (0–100),
 * and sending the file to the backend for resize + compression. Displays
 * original and processed images side-by-side with file sizes and
 * size-reduction percentage, and offers a download link for the result.
 *
 * @module App
 *
 * Features:
 * - File picker (PNG, JPG, GIF) with client-side type validation
 * - Quality slider for JPEG compression (form field `quality`)
 * - Preview of selected image before upload
 * - Success/error messages and loading state
 * - Reset to clear selection and results
 *
 * API:
 * - Backend base URL from `import.meta.env.VITE_API_URL` (default: http://localhost:5000)
 * - POST /upload with FormData: `image` (file), `quality` (number)
 * - Processed image URL: `${API_URL}/uploads/${processed_image}`
 */
import { useState } from 'react'
import './App.css'

// Helper function to format file size
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Root component: upload form, quality slider, and original vs processed image display.
 * No props. Renders the main app UI inside a single root div (app-container).
 * @returns {JSX.Element}
 */
function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [quality, setQuality] = useState(50)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [processedImage, setProcessedImage] = useState(null)
  const [originalSize, setOriginalSize] = useState(null)
  const [processedSize, setProcessedSize] = useState(null)
  const [sizeReduction, setSizeReduction] = useState(null)

  // Backend endpoint - loaded from environment variable
  // Set VITE_API_URL in .env.local file (see .env.example for template)
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']
      if (!allowedTypes.includes(file.type)) {
        setError('Please select a valid image file (PNG, JPG, or GIF)')
        setSelectedFile(null)
        setPreview(null)
        return
      }

      setSelectedFile(file)
      setOriginalSize(file.size)
      setError(null)
      setMessage(null)
      setProcessedImage(null)
      setProcessedSize(null)
      setSizeReduction(null)

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!selectedFile) {
      setError('Please select an image file')
      return
    }

    setLoading(true)
    setError(null)
    setMessage(null)
    setProcessedImage(null)

    try {
      // Create FormData to send file
      const formData = new FormData()
      formData.append('image', selectedFile)
      formData.append('quality', quality.toString())

      // Send to backend
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed')
      }

      setMessage(data.message || 'Image uploaded successfully!')
      // Set the processed image URL and file sizes
      if (data.processed_image) {
        setProcessedImage(`${API_URL}/uploads/${data.processed_image}`)
      }
      if (data.original_size !== undefined) {
        setOriginalSize(data.original_size)
      }
      if (data.processed_size !== undefined) {
        setProcessedSize(data.processed_size)
      }
      if (data.size_reduction_percent !== undefined) {
        setSizeReduction(data.size_reduction_percent)
      }
    } catch (err) {
      setError(err.message || 'Failed to upload image. Make sure the backend server is running.')
      console.error('Upload error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreview(null)
    setQuality(50)
    setMessage(null)
    setError(null)
    setProcessedImage(null)
    setOriginalSize(null)
    setProcessedSize(null)
    setSizeReduction(null)
  }

  return (
    <div className="app-container">
      <h1>Image Optimizer</h1>
      <p className="subtitle">Upload an image to optimize and resize</p>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="image-upload" className="file-label">
            <span className="file-label-text">
              {selectedFile ? selectedFile.name : 'Choose an image file'}
            </span>
            <input
              id="image-upload"
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/gif"
              onChange={handleFileChange}
              className="file-input"
              disabled={loading}
            />
          </label>
        </div>

          <div className="form-group">
          <label htmlFor="quality" className="quality-label">
            Quality: {quality}%
          </label>
          <input
            id="quality"
            type="range"
            min="0"
            max="100"
            value={quality}
            onChange={(e) => setQuality(Number(e.target.value))}
            className="quality-slider"
            disabled={loading}
          />
        </div>

        <div className="button-group">
          <button
            type="submit"
            disabled={!selectedFile || loading}
            className="submit-button"
          >
            {loading ? 'Uploading...' : 'Upload & Optimize'}
          </button>
          {(selectedFile || message || error) && (
            <button
              type="button"
              onClick={handleReset}
              className="reset-button"
              disabled={loading}
            >
              Reset
            </button>
          )}
        </div>
      </form>

      {error && (
        <div className="message error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {message && (
        <div className="message success">
          <strong>Success:</strong> {message}
        </div>
      )}

      {(preview || processedImage) && (
        <div className="images-grid">
          {preview && (
            <div className="grid-item">
              <h3>Original Image</h3>
              {originalSize && (
                <div className="file-size-info">
                  <span className="file-size-label">File Size:</span>
                  <span className="file-size-value">{formatFileSize(originalSize)}</span>
                </div>
              )}
              <div className="image-wrapper">
                <img src={preview} alt="Preview" className="grid-image" />
              </div>
            </div>
          )}
          
          {processedImage && (
            <div className="grid-item">
              <h3>Processed Image</h3>
              {processedSize && (
                <div className="file-size-info">
                  <span className="file-size-label">File Size:</span>
                  <span className="file-size-value">{formatFileSize(processedSize)}</span>
                </div>
              )}
              {sizeReduction !== null && (
                <div className={`size-reduction ${sizeReduction > 0 ? 'positive' : 'negative'}`}>
                  <span className="reduction-label">
                    {sizeReduction > 0 ? 'Size Reduction:' : 'Size Increase:'}
                  </span>
                  <span className="reduction-value">
                    {sizeReduction > 0 ? '-' : '+'}{Math.abs(sizeReduction).toFixed(2)}%
                  </span>
                </div>
              )}
              <div className="image-wrapper">
                <img src={processedImage} alt="Processed" className="grid-image" />
              </div>
              <a
                href={processedImage}
                download
                className="download-link"
              >
                Download Processed Image
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
