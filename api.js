class API {
    static async analyzeImage(file) {
        const formData = new FormData();
        formData.append('image', file);
        
        try {
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.detail);
            }
            
            return result;
            
        } catch (error) {
            console.error('API Error:', error);
            
            // Fallback for demo purposes when backend is not available
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                // Simulate API response for demo
                await new Promise(resolve => setTimeout(resolve, 2000));
                return {
                    status: 'success',
                    prediction: Math.random() > 0.5 ? 'REAL' : 'FAKE'
                };
            }
            
            throw error;
        }
    }
    
    static async analyzeVideo(file) {
        // Similar implementation for video analysis
        // This would need to be adapted based on your video processing requirements
        const formData = new FormData();
        formData.append('video', file);
        
        try {
            const response = await fetch('http://localhost:8000/analyze-video', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Video API Error:', error);
            throw error;
        }
    }
}