/**
 * 👂-Say Shared Utilities
 * 
 * Common utility functions shared across the application
 */

/**
 * URL parameter and game key utilities
 */
const URLUtils = {
    /**
     * Get URL parameter value by name
     */
    getParameter(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    },

    /**
     * Create URL-safe game key from timestamp
     */
    encodeGameKey(gameStartTime) {
        return btoa(gameStartTime.toString()).replace(/[+=\/]/g, '');
    },

    /**
     * Decode URL-safe game key back to timestamp
     */
    decodeGameKey(gameKey) {
        try {
            // Add padding if needed for base64
            const padded = gameKey + '=='.slice(0, (4 - gameKey.length % 4) % 4);
            const decoded = atob(padded);
            const timestamp = parseInt(decoded);
            return isNaN(timestamp) ? null : timestamp;
        } catch (error) {
            console.error('Failed to decode game key:', error);
            return null;
        }
    },

    /**
     * Update URL with parameters without page reload
     */
    updateURL(params) {
        const url = new URL(window.location);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                url.searchParams.set(key, value);
            }
        });
        window.history.replaceState({}, '', url);
    },

    /**
     * Clear specific parameters from URL
     */
    clearParams(paramNames) {
        const url = new URL(window.location);
        paramNames.forEach(name => url.searchParams.delete(name));
        window.history.replaceState({}, '', url);
    }
};

/**
 * LocalStorage service for centralized clip management
 */
class StorageService {
    static STORAGE_KEY = 'hearsayClips';

    /**
     * Get all clips from localStorage
     */
    static getAllClips() {
        return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
    }

    /**
     * Save a new clip to localStorage
     */
    static saveClip(clip) {
        const existingClips = this.getAllClips();
        existingClips.push(clip);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(existingClips));
        console.log('Clip saved to localStorage:', clip.id);
    }

    /**
     * Update an existing clip in localStorage
     */
    static updateClip(updatedClip) {
        const existingClips = this.getAllClips();
        const clipIndex = existingClips.findIndex(clip => clip.id === updatedClip.id);
        
        if (clipIndex !== -1) {
            existingClips[clipIndex] = updatedClip;
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(existingClips));
            console.log('Clip updated in localStorage:', updatedClip.id);
            return true;
        } else {
            console.warn('Clip not found for update:', updatedClip.id);
            return false;
        }
    }

    /**
     * Get clips for a specific game session
     */
    static getClipsByGame(gameStartTime) {
        const allClips = this.getAllClips();
        return allClips.filter(clip => clip.gameStartTime === gameStartTime);
    }

    /**
     * Delete clips by IDs
     */
    static deleteClips(clipIds) {
        const existingClips = this.getAllClips();
        const filteredClips = existingClips.filter(clip => !clipIds.includes(clip.id));
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filteredClips));
        console.log('Clips deleted:', clipIds);
    }

    /**
     * Clear all clips from localStorage
     */
    static clearAllClips() {
        localStorage.removeItem(this.STORAGE_KEY);
        console.log('All clips cleared from localStorage');
    }
}

/**
 * Game configuration constants
 */
const GAME_CONFIG = {
    DELAYS: {
        TARGET_RESUME: 1000,    // Delay before resuming target playback after attempt
        PLAYBACK_LOOP: 1000,    // Pause between target playback loops
        PLAY_ALL: 1000          // Pause between clips in play-all sequence
    },
    
    PHASES: {
        INITIAL: 'initial',
        TARGET_RECORDED: 'target_recorded', 
        PLAYING_ATTEMPTS: 'playing_attempts',
        FINISHED: 'finished'
    },
    
    CLIP_TYPES: {
        TARGET: 'target',
        ATTEMPT: 'attempt'
    },
    
    UI: {
        RECORDING_BUTTON_TEXT: '⏹️',
        IDLE_BUTTON_TEXT: '🎤',
        STOP_BUTTON_TEXT: '⏹️ Stop',
        PLAY_ALL_BUTTON_TEXT: '⏹️ Stop'
    }
};

/**
 * Clip metadata factory for consistent clip creation
 */
class ClipMetadata {
    /**
     * Create metadata for a target clip
     */
    static createTarget(gameStartTime, recordingStartTime, base64Data) {
        return {
            id: recordingStartTime,
            data: base64Data,
            timestamp: new Date().toISOString(),
            size: base64Data.length,
            // Game-specific metadata
            gameStartTime: gameStartTime,
            clipType: GAME_CONFIG.CLIP_TYPES.TARGET,
            recordingStartTime: recordingStartTime,
            gameClipIndex: 0,
            gameFinished: false
        };
    }

    /**
     * Create metadata for an attempt clip
     */
    static createAttempt(gameStartTime, recordingStartTime, base64Data, attemptIndex) {
        return {
            id: recordingStartTime,
            data: base64Data,
            timestamp: new Date().toISOString(),
            size: base64Data.length,
            // Game-specific metadata
            gameStartTime: gameStartTime,
            clipType: GAME_CONFIG.CLIP_TYPES.ATTEMPT,
            recordingStartTime: recordingStartTime,
            gameClipIndex: attemptIndex + 1
        };
    }

    /**
     * Create metadata for a regular (non-game) clip
     */
    static createRegular(recordingStartTime, base64Data) {
        return {
            id: recordingStartTime,
            data: base64Data,
            timestamp: new Date().toISOString(),
            size: base64Data.length,
            // No game-specific metadata for regular clips
            clipType: 'regular'
        };
    }

    /**
     * Mark a clip as part of a finished game
     */
    static markFinished(clip) {
        return {
            ...clip,
            gameFinished: true
        };
    }
}

/**
 * Game state management class
 */
class GameState {
    constructor() {
        this.phase = GAME_CONFIG.PHASES.INITIAL;
        this.gameStartTime = null;
        this.targetClip = null;
        this.attemptClips = [];
    }

    /**
     * Check if recording is currently allowed
     */
    canRecord() {
        return this.phase !== GAME_CONFIG.PHASES.FINISHED;
    }

    /**
     * Check if the game is finished
     */
    isFinished() {
        return this.phase === GAME_CONFIG.PHASES.FINISHED;
    }

    /**
     * Check if target clip has been recorded
     */
    hasTarget() {
        return this.targetClip !== null;
    }

    /**
     * Get the next attempt index
     */
    getNextAttemptIndex() {
        return this.attemptClips.length;
    }

    /**
     * Reset all game state
     */
    reset() {
        this.phase = GAME_CONFIG.PHASES.INITIAL;
        this.gameStartTime = null;
        this.targetClip = null;
        this.attemptClips = [];
    }

    /**
     * Set target clip and update phase
     */
    setTarget(targetClip) {
        this.targetClip = targetClip;
        this.gameStartTime = targetClip.gameStartTime;
        this.phase = GAME_CONFIG.PHASES.TARGET_RECORDED;
    }

    /**
     * Add attempt clip
     */
    addAttempt(attemptClip) {
        this.attemptClips.push(attemptClip);
    }

    /**
     * Mark game as finished
     */
    finish() {
        this.phase = GAME_CONFIG.PHASES.FINISHED;
    }

    /**
     * Get all clips in the correct order
     */
    getAllClips() {
        return this.targetClip ? [this.targetClip, ...this.attemptClips] : [...this.attemptClips];
    }

    /**
     * Restore state from storage
     */
    restoreFromStorage(gameStartTime) {
        const gameClips = StorageService.getClipsByGame(gameStartTime);
        
        if (gameClips.length === 0) {
            return false;
        }

        // Separate and sort clips
        const targetClip = gameClips.find(clip => clip.clipType === GAME_CONFIG.CLIP_TYPES.TARGET);
        const attemptClips = gameClips
            .filter(clip => clip.clipType === GAME_CONFIG.CLIP_TYPES.ATTEMPT)
            .sort((a, b) => a.gameClipIndex - b.gameClipIndex);

        if (!targetClip) {
            return false;
        }

        // Restore state
        this.gameStartTime = gameStartTime;
        this.targetClip = targetClip;
        this.attemptClips = attemptClips;
        
        // Determine phase
        this.phase = targetClip.gameFinished 
            ? GAME_CONFIG.PHASES.FINISHED 
            : GAME_CONFIG.PHASES.TARGET_RECORDED;

        return true;
    }
}

/**
 * Microphone Permission Management
 */
const MicrophonePermissions = {
    /**
     * Check current microphone permission status
     */
    async checkPermission() {
        try {
            const result = await navigator.permissions.query({ name: 'microphone' });
            return result.state; // 'granted', 'denied', or 'prompt'
        } catch (error) {
            // Fallback for browsers that don't support permissions API
            console.warn('Permissions API not supported, will try direct access');
            return 'unknown';
        }
    },

    /**
     * Request microphone permission by attempting to get user media
     */
    async requestPermission() {
        try {
            console.log('Attempting to request microphone permission...');
            console.log('Navigator available:', !!navigator);
            console.log('MediaDevices available:', !!(navigator.mediaDevices));
            console.log('getUserMedia available:', !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia));
            console.log('Current URL protocol:', window.location.protocol);
            console.log('Is secure context:', window.isSecureContext);
            
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('getUserMedia not supported');
            }
            
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log('Microphone permission granted successfully');
            // Stop the stream immediately since we only wanted permission
            stream.getTracks().forEach(track => track.stop());
            return 'granted';
        } catch (error) {
            console.error('Microphone permission denied:', error);
            console.log('Error name:', error.name);
            console.log('Error message:', error.message);
            return 'denied';
        }
    },

    /**
     * Check and request microphone permission if needed
     * Returns the permission status and updates UI accordingly
     */
    async ensurePermission(statusElement) {
        const currentStatus = await this.checkPermission();
        
        if (currentStatus === 'granted') {
            if (statusElement) {
                statusElement.textContent = statusElement.getAttribute('data-ready-text') || 'Ready to record';
                statusElement.className = 'status ready';
            }
            return 'granted';
        }

        if (currentStatus === 'denied') {
            if (statusElement) {
                statusElement.textContent = '🚫 Microphone access denied. Please enable in browser settings.';
                statusElement.className = 'status error';
            }
            return 'denied';
        }

        // Permission needed (prompt or unknown status)
        if (statusElement) {
            statusElement.textContent = '🎤 Requesting microphone access...';
            statusElement.className = 'status requesting';
        }

        const result = await this.requestPermission();
        
        if (result === 'granted') {
            if (statusElement) {
                statusElement.textContent = statusElement.getAttribute('data-ready-text') || 'Ready to record';
                statusElement.className = 'status ready';
            }
        } else {
            if (statusElement) {
                // Provide more specific error messages
                if (window.location.protocol === 'file:') {
                    statusElement.textContent = '🚫 Microphone requires HTTP/HTTPS. Try: http://localhost:3001';
                } else if (!window.isSecureContext && window.location.protocol === 'http:') {
                    statusElement.textContent = '🚫 Microphone may require HTTPS in some browsers';
                } else {
                    statusElement.textContent = '🚫 Microphone access denied. Check browser permissions.';
                }
                statusElement.className = 'status error';
            }
        }

        return result;
    }
}
