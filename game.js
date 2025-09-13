/**
 * Banana Phone JavaScript
 * 
 * This file contains the game logic for the reverse audio copycat game.
 * 
 * GAME FLOW:
 * 1. User records a "target" clip
 * 2. Target clip plays in reverse on loop with 2-second pauses
 * 3. Users record "attempt" clips trying to mimic the reversed target
 * 4. Game ends when "Finish" button is pressed
 * 5. All clips are displayed and can be played back (in revers        console.log('Target clip recorded:', targetClip);
        this.status.textContent = `Tap and try to imitate it! (Turn up your volume)`;
        // this.status.textContent = 'Target recorded! Recording your attempts...';
        
        // Start target playback loop after 1 second delay
 * STORAGE FORMAT:
 * Each clip has metadata:
 * - gameStartTime: Timestamp when the game session started
 * - clipType: "target" or "attempt"
 * - recordingStartTime: When this specific recording began
 * - gameClipIndex: Order within the game (0 for target, 1+ for attempts)
 */

class GameController {
    constructor() {
        // Use centralized game state management
        this.gameState = new GameState();
        
        // Recording and playback state  
        this.isRecording = false;
        this.isPlayingTarget = false;
        this.targetPlaybackInterval = null;
        this.currentTargetSource = null;
        
        // Audio context (reuse from main recorder if available)
        this.audioContext = null;
        
        // DOM elements
        this.recordButton = document.getElementById('recordButton');
        this.status = document.getElementById('status');
        this.recorderSection = document.querySelector('.recorder-section'); // Add recorder section for hiding
        this.startOverSection = document.getElementById('startOverSection');
        this.startOverButton = document.getElementById('startOverButton');
        this.finishSection = document.getElementById('finishSection');
        this.finishButton = document.getElementById('finishButton');
        this.resultsSection = document.getElementById('resultsSection');
        this.playAllButton = document.getElementById('playAllButton');
        this.gameClipsList = document.getElementById('gameClipsList');
        
        // Modal elements
        this.gameRestoreModal = document.getElementById('gameRestoreModal');
        this.attemptCountSpan = document.getElementById('attemptCount');
        this.continueGameButton = document.getElementById('continueGameButton');
        this.startOverModalButton = document.getElementById('startOverModalButton');
        
        // Recording state (similar to main AudioRecorder)
        this.mediaRecorder = null;
        this.chunks = [];
        
        // Playback state for results section
        this.isPlayingAll = false;
        this.currentPlayAllIndex = 0;
        this.playAllTimeout = null;
        
        this.init();
    }

    /**
     * Initialize the game controller
     * Sets up audio context and event listeners
     */
    async init() {
        try {
            // Initialize audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            console.log('Game AudioContext created:', this.audioContext.state);
            
            this.setupEventListeners();
            
            // Check for existing game from URL parameter
            this.checkForExistingGame();
            
            console.log('Game controller initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize game controller:', error);
            this.status.textContent = 'Failed to initialize game system';
            this.recordButton.disabled = true;
        }
    }

    /**
     * Check for existing game from URL parameter on page load
     * Restores game state if a valid game is found
     */
    checkForExistingGame() {
        console.log('Checking for existing game in URL...');
        const gameKey = URLUtils.getParameter('game');
        if (!gameKey) {
            console.log('No game parameter found in URL');
            return;
        }
        
        console.log('Found game parameter:', gameKey);
        
        // Convert URL-safe game key back to timestamp
        const gameStartTime = URLUtils.decodeGameKey(gameKey);
        if (!gameStartTime) {
            console.log('Invalid game key format');
            return;
        }
        
        // Try to restore the game using centralized state management
        this.restoreGameFromStorage(gameStartTime);
    }



    /**
     * Restore game state from localStorage using gameStartTime
     */
    restoreGameFromStorage(gameStartTime) {
        // Use centralized game state restoration
        const restored = this.gameState.restoreFromStorage(gameStartTime);
        
        if (!restored) {
            console.log('Failed to restore game:', gameStartTime);
            return;
        }
        
        // Always show the modal for restored games (both in-progress and finished)
        this.showGameRestoreModal();
        
        console.log(`Game restored: ${this.gameState.attemptClips.length} attempts, phase: ${this.gameState.phase}`);
    }

    /**
     * Create a test game for development - adds sample clips to localStorage
     * TODO: Remove this method in production
     */
    createTestGame() {
        const gameStartTime = 1726156800000;
        const gameKey = URLUtils.encodeGameKey(gameStartTime);
        
        // Create test clips
        const targetClip = ClipMetadata.createTarget(gameStartTime, gameStartTime + 1000, 'data:audio/webm;base64,test');
        const attempt1 = ClipMetadata.createAttempt(gameStartTime, gameStartTime + 5000, 'data:audio/webm;base64,test1', 0);
        const attempt2 = ClipMetadata.createAttempt(gameStartTime, gameStartTime + 8000, 'data:audio/webm;base64,test2', 1);
        
        // Save to storage
        StorageService.saveClip(targetClip);
        StorageService.saveClip(attempt1);
        StorageService.saveClip(attempt2);
        
        // Update URL and reload to test modal
        URLUtils.updateURL({ game: gameKey });
        console.log('Test game created. Reload page to see modal:', window.location.href);
        
        return { gameStartTime, gameKey, clips: [targetClip, attempt1, attempt2] };
    }

    /**
     * Show UI for restored game that's still in progress
     */
    showRestoredGameInProgress() {
        this.status.textContent = `Game restored! ${this.gameState.attemptClips.length} attempts recorded. Continue recording or finish.`;
        this.startOverSection.style.display = 'block';
        this.finishSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.recorderSection.style.display = 'block';
        
        // Resume target playback
        setTimeout(() => {
            this.startTargetPlaybackLoop();
        }, GAME_CONFIG.DELAYS.TARGET_RESUME);
    }

    /**
     * Update URL with game key parameter for refresh persistence
     */
    updateUrlWithGameKey() {
        if (!this.gameState.gameStartTime) {
            console.warn('No game start time available for URL update');
            return;
        }
        
        const gameKey = URLUtils.encodeGameKey(this.gameState.gameStartTime);
        URLUtils.updateURL({ game: gameKey });
        console.log('URL updated with game key:', gameKey);
    }

    /**
     * Clear game parameter from URL
     */
    clearUrlGameKey() {
        URLUtils.clearParams(['game']);
        console.log('Game key cleared from URL');
    }

    /**
     * Show the game restore modal for both in-progress and finished games
     */
    showGameRestoreModal() {
        // Update modal content based on game state
        if (this.gameState.isFinished()) {
            // Finished game - update modal for playback
            const modalTitle = document.querySelector('#gameRestoreModal h2');
            const modalText = document.querySelector('#gameRestoreModal p');
            
            if (modalTitle) modalTitle.textContent = '🎉 Welcome back!';
            if (modalText) modalText.innerHTML = `View your game or start a new one?`;
        } else {
            // In-progress game - original modal content
            const modalTitle = document.querySelector('#gameRestoreModal h2');
            const modalText = document.querySelector('#gameRestoreModal p');
            
            if (modalTitle) modalTitle.textContent = '👋 Hi! Continue your game or start over?';
            if (modalText) modalText.innerHTML = `You have a game in progress with <span id="attemptCount">${this.gameState.attemptClips.length}</span> copycats recorded.`;
        }
        
        // Ensure attempt count is updated (in case the span reference changed)
        const updatedAttemptSpan = document.getElementById('attemptCount');
        if (updatedAttemptSpan) updatedAttemptSpan.textContent = this.gameState.attemptClips.length;
        
        // Show the modal
        this.gameRestoreModal.style.display = 'flex';
        
        const gameType = this.gameState.isFinished() ? 'finished' : 'in-progress';
        console.log(`Showing restore modal for ${gameType} game with ${this.gameState.attemptClips.length} attempts`);
    }

    /**
     * Hide the game restore modal
     */
    hideGameRestoreModal() {
        this.gameRestoreModal.style.display = 'none';
    }

    /**
     * Continue the existing game (called from modal)
     */
    continueExistingGame() {
        console.log('Continuing existing game');
        
        // Hide the modal
        this.hideGameRestoreModal();
        
        // Handle based on game state
        if (this.gameState.isFinished()) {
            // For finished games, show results and start playing all
            this.showRestoredGameFinished();
            // Auto-start playing all clips after showing results
            setTimeout(() => {
                this.startPlayAll();
            }, 500);
        } else {
            // For in-progress games, show the game UI
            this.showRestoredGameInProgress();
        }
    }

    /**
     * Start over from the modal (clear URL and refresh)
     */
    startOverFromModal() {
        console.log('Starting over from modal');
        
        // Clear the URL parameter
        this.clearUrlGameKey();
        
        // Refresh the page to start fresh
        window.location.reload();
    }

    /**

    /**
     * Show UI for restored game that's finished
     */
    showRestoredGameFinished() {
        this.status.textContent = 'Game restored - viewing results';
        this.startOverSection.style.display = 'block';
        this.finishSection.style.display = 'none';
        this.recorderSection.style.display = 'none';
        this.showGameResults();
    }

    /**
     * Set up all event listeners for game interactions
     */
    setupEventListeners() {
        // Main record button - handles both target and attempt recordings
        this.recordButton.addEventListener('click', () => this.handleRecordButtonClick());
        
        // Start over button - resets the entire game
        this.startOverButton.addEventListener('click', () => this.startNewGame());
        
        // Finish button - ends current game and shows results
        this.finishButton.addEventListener('click', () => this.finishGame());
        
        // Play all button - plays all attempts in sequence
        this.playAllButton.addEventListener('click', () => this.togglePlayAll());
        
        // Modal buttons
        this.continueGameButton.addEventListener('click', () => this.continueExistingGame());
        this.startOverModalButton.addEventListener('click', () => this.startOverFromModal());
        
        console.log('Game event listeners set up');
    }

    /**
     * Handle clicks on the main record button
     * Behavior changes based on current game phase
     */
    async handleRecordButtonClick() {
        if (this.isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    /**
     * Start recording audio
     * Stops target playback if it's currently playing
     */
    async startRecording() {
        try {
            console.log('Starting game recording...');
            
            // Stop target playback if it's currently playing
            this.stopTargetPlayback();
            
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.chunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                console.log('Game audio data chunk received:', event.data.size, 'bytes');
                this.chunks.push(event.data);
            };
            
            this.mediaRecorder.onstart = () => {
                console.log('Game MediaRecorder started');
                this.status.textContent = '🔴 Recording... Click to stop';
            };
            
            this.mediaRecorder.onstop = () => {
                console.log('Game recording stopped, processing audio...');
                this.processRecording();
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            this.recordButton.classList.add('recording');
            this.recordButton.textContent = GAME_CONFIG.UI.RECORDING_BUTTON_TEXT;
            this.status.textContent = 'Starting recording...';
            
        } catch (error) {
            console.error('Failed to start game recording:', error);
            this.status.textContent = 'Failed to start recording';
        }
    }

    /**
     * Stop the current recording
     */
    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            console.log('Stopping game recording...');
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            this.recordButton.classList.remove('recording');
            this.recordButton.textContent = GAME_CONFIG.UI.IDLE_BUTTON_TEXT;
            this.status.textContent = 'Processing recording...';
        }
    }

    /**
     * Process the completed recording
     * Determines whether this is a target or attempt clip based on game phase
     */
    async processRecording() {
        try {
            const blob = new Blob(this.chunks, { type: 'audio/webm' });
            console.log('Created game audio blob:', blob.size, 'bytes, type:', blob.type);
            
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64Data = reader.result;
                const recordingStartTime = Date.now();
                
                if (this.gameState.phase === GAME_CONFIG.PHASES.INITIAL) {
                    // This is the target clip
                    this.processTargetClip(base64Data, recordingStartTime);
                } else if (this.gameState.phase === GAME_CONFIG.PHASES.TARGET_RECORDED) {
                    // This is an attempt clip
                    this.processAttemptClip(base64Data, recordingStartTime);
                }
            };
            
            reader.readAsDataURL(blob);
            
        } catch (error) {
            console.error('Failed to process game recording:', error);
            this.status.textContent = 'Failed to save recording';
        }
    }

    /**
     * Process the target clip (first recording of the game)
     * Starts a new game session and begins target playback loop
     */
    processTargetClip(base64Data, recordingStartTime) {
        // Start a new game session
        const gameStartTime = Date.now();
        
        // Create target clip using metadata factory
        const targetClip = ClipMetadata.createTarget(gameStartTime, recordingStartTime, base64Data);
        
        // Save using centralized storage service
        StorageService.saveClip(targetClip);
        
        // Update game state
        this.gameState.setTarget(targetClip);
        
        // Update URL with game key for refresh persistence
        this.updateUrlWithGameKey();
        
        console.log('Target clip recorded:', targetClip);
        this.status.textContent = `Tap and try to imitate it! (Turn up your volume)`;
        // this.status.textContent = 'Target recorded! Recording your attempts...';
        this.startOverSection.style.display = 'block';
        
        // Start target playback loop after 1 second delay
        setTimeout(() => {
            this.startTargetPlaybackLoop();
        }, 1000);
    }

    /**
     * Process an attempt clip (subsequent recordings)
     * Adds to the attempt clips array and resumes target playback
     */
    processAttemptClip(base64Data, recordingStartTime) {
        // Create attempt clip using metadata factory
        const attemptIndex = this.gameState.getNextAttemptIndex();
        const attemptClip = ClipMetadata.createAttempt(
            this.gameState.gameStartTime, 
            recordingStartTime, 
            base64Data, 
            attemptIndex
        );
        
        // Add to game state and save
        this.gameState.addAttempt(attemptClip);
        StorageService.saveClip(attemptClip);
        
        console.log('Attempt clip recorded:', attemptClip);
        
        // Show finish button after first attempt
        if (this.gameState.attemptClips.length === 1) {
            this.finishSection.style.display = 'block';
        }
        
        // Update status
        this.status.textContent = `Attempt ${this.gameState.attemptClips.length} recorded! Record another or finish the game.`;
        
        // Resume target playback after configured delay
        setTimeout(() => {
            this.startTargetPlaybackLoop();
        }, GAME_CONFIG.DELAYS.TARGET_RESUME);
    }



    /**
     * Start the target clip playback loop
     * Plays the target clip in reverse with 2-second pauses between loops
     */
    async startTargetPlaybackLoop() {
        if (!this.gameState.targetClip || this.isRecording || this.gameState.isFinished()) {
            return;
        }
        
        this.isPlayingTarget = true;
        console.log('Starting target playback loop');
        
        // Function to play target once
        const playTargetOnce = async () => {
            if (!this.isPlayingTarget) return;
            
            try {
                // Resume audio context if needed
                if (this.audioContext.state === 'suspended') {
                    await this.audioContext.resume();
                }
                
                // Decode the target clip
                const response = await fetch(this.gameState.targetClip.data);
                const arrayBuffer = await response.arrayBuffer();
                const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
                
                // Create reversed audio buffer
                const reversedBuffer = this.reverseAudioBuffer(audioBuffer);
                
                // Create and play source
                const source = this.audioContext.createBufferSource();
                source.buffer = reversedBuffer;
                source.connect(this.audioContext.destination);
                
                this.currentTargetSource = source;
                
                source.onended = () => {
                    this.currentTargetSource = null;
                    
                    // Schedule next playback after configured delay if still playing
                    if (this.isPlayingTarget) {
                        this.targetPlaybackInterval = setTimeout(() => {
                            playTargetOnce();
                        }, GAME_CONFIG.DELAYS.PLAYBACK_LOOP);
                    }
                };
                
                source.start(0);
                
            } catch (error) {
                console.error('Error playing target clip:', error);
                this.stopTargetPlayback();
            }
        };
        
        // Start the first playback
        playTargetOnce();
    }

    /**
     * Stop the target clip playback loop
     */
    stopTargetPlayback() {
        this.isPlayingTarget = false;
        
        if (this.currentTargetSource) {
            this.currentTargetSource.stop();
            this.currentTargetSource = null;
        }
        
        if (this.targetPlaybackInterval) {
            clearTimeout(this.targetPlaybackInterval);
            this.targetPlaybackInterval = null;
        }
        
        console.log('Target playback stopped');
    }

    /**
     * Start a completely new game
     * Resets all game state and hides UI elements
     */
    startNewGame() {
        console.log('Starting new game');
        
        // Stop any current playback
        this.stopTargetPlayback();
        this.stopPlayAll();
        
        // Reset game state using centralized management
        this.gameState.reset();
        
        // Clear game parameter from URL
        this.clearUrlGameKey();
        
        // Reset UI
        this.status.textContent = 'Tap to record something for your friends to imitate!';
        this.startOverSection.style.display = 'none';
        this.finishSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.recorderSection.style.display = 'block';
        
        // Ensure record button is in correct state
        this.recordButton.classList.remove('recording');
        this.recordButton.textContent = GAME_CONFIG.UI.IDLE_BUTTON_TEXT;
    }

    /**
     * Finish the current game
     * Stops target playback and shows results
     */
    finishGame() {
        console.log('Finishing game');
        
        // Stop target playback
        this.stopTargetPlayback();
        
        // Mark game as finished using centralized state management
        if (this.gameState.targetClip) {
            const finishedClip = ClipMetadata.markFinished(this.gameState.targetClip);
            StorageService.updateClip(finishedClip);
            this.gameState.targetClip = finishedClip; // Update local copy
        }
        
        // Update game phase
        this.gameState.finish();
        
        // Hide game controls and recorder
        this.finishSection.style.display = 'none';
        this.recorderSection.style.display = 'none';
        
        // Show results
        this.showGameResults();
    }

    /**
     * Display the game results
     * Shows all clips from the current game with playback controls
     */
    showGameResults() {
        this.resultsSection.style.display = 'block';
        
        // Show the "Play Again" button after finish
        this.startOverSection.style.display = 'block';
        
        // Compile all clips from current game using centralized state
        const allGameClips = this.gameState.getAllClips();
        
        // Render clips list
        this.gameClipsList.innerHTML = allGameClips.map((clip, index) => {
            const isTarget = clip.clipType === GAME_CONFIG.CLIP_TYPES.TARGET;
            const label = isTarget ? 'Original' : `Copycat #${clip.gameClipIndex}`;
            const clipClass = isTarget ? 'target-clip' : 'attempt-clip';
            const defaultReversed = !isTarget; // Attempts default to reversed, target defaults to normal
            
            return `
                <div class="game-clip-item ${clipClass}">
                    <div class="game-clip-header">
                        <span class="game-clip-label">${label}</span>
                        <div class="game-clip-controls">
                            <button class="game-clip-button" onclick="gameController.playGameClip(${clip.id})">
                                ▶️
                            </button>
                            <button class="game-clip-button" onclick="gameController.stopGameClip(${clip.id})">
                                ⏹️
                            </button>
                            <label class="reverse-checkbox">
                                <input type="checkbox" id="reverse-${clip.id}" ${defaultReversed ? 'checked' : ''}>
                                Reverse
                            </label>
                        </div>
                    </div>
                    <div class="game-clip-info">
                        Recorded: ${new Date(clip.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            `;
        }).join('');
        
        // Auto-start playing all clips after showing results
        setTimeout(() => {
            this.startPlayAll();
        }, 500); // Small delay to let the DOM update
        
        console.log('Game results displayed');
    }

    /**
     * Play a specific game clip in reverse
     */
    async playGameClip(clipId) {
        try {
            // Find the clip using centralized state
            const allClips = this.gameState.getAllClips();
            const clip = allClips.find(c => c.id === clipId);
            
            if (!clip) {
                console.error('Game clip not found:', clipId);
                return;
            }
            
            // Stop any other playback
            this.stopAllGameClipPlayback();
            
            // Check if reverse checkbox is checked
            const reverseCheckbox = document.getElementById(`reverse-${clipId}`);
            const shouldReverse = reverseCheckbox ? reverseCheckbox.checked : false;
            
            console.log('Playing game clip:', clipId, shouldReverse ? '(reversed)' : '(normal)');
            
            // Resume audio context if needed
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            // Decode and optionally reverse the clip
            const response = await fetch(clip.data);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            const finalBuffer = shouldReverse ? this.reverseAudioBuffer(audioBuffer) : audioBuffer;
            
            const source = this.audioContext.createBufferSource();
            source.buffer = finalBuffer;
            source.connect(this.audioContext.destination);
            
            // Store source for stopping
            clip.currentSource = source;
            
            source.onended = () => {
                clip.currentSource = null;
                console.log('Game clip playback completed');
            };
            
            source.start(0);
            
        } catch (error) {
            console.error('Failed to play game clip:', error);
        }
    }

    /**
     * Stop playback of a specific game clip
     */
    stopGameClip(clipId) {
        const allClips = this.gameState.getAllClips();
        const clip = allClips.find(c => c.id === clipId);
        
        if (clip && clip.currentSource) {
            clip.currentSource.stop();
            clip.currentSource = null;
            console.log('Stopped game clip:', clipId);
        }
    }

    /**
     * Stop all game clip playback
     */
    stopAllGameClipPlayback() {
        const allClips = this.gameState.getAllClips();
        allClips.forEach(clip => {
            if (clip.currentSource) {
                clip.currentSource.stop();
                clip.currentSource = null;
            }
        });
    }

    /**
     * Toggle play all functionality
     * Plays all attempt clips in sequence with 2-second pauses
     */
    togglePlayAll() {
        if (this.isPlayingAll) {
            this.stopPlayAll();
        } else {
            this.startPlayAll();
        }
    }

    /**
     * Start playing all clips in sequence (target first, then attempts)
     */
    startPlayAll() {
        if (!this.gameState.targetClip) {
            console.log('No target clip to play');
            return;
        }
        
        this.isPlayingAll = true;
        this.currentPlayAllIndex = -1; // Start with -1 to play target first
        this.playAllButton.textContent = '⏹️ Stop Loop';
        
        console.log('Starting play all sequence (target + attempts) - will loop continuously');
        this.playNextInSequence();
    }

    /**
     * Play the next clip in the play-all sequence
     */
    async playNextInSequence() {
        if (!this.isPlayingAll) {
            return;
        }
        
        // Check if we've reached the end and should loop back
        if (this.currentPlayAllIndex >= this.gameState.attemptClips.length) {
            console.log('Looping back to start of play-all sequence');
            this.currentPlayAllIndex = -1; // Reset to play target clip first
        }
        
        // Determine which clip to play and whether to reverse it
        let clip, shouldReverse, logMessage;
        if (this.currentPlayAllIndex === -1) {
            // Play target clip normally
            clip = this.gameState.targetClip;
            shouldReverse = false;
            logMessage = 'Playing target clip in loop sequence';
        } else {
            // Play attempt clip reversed
            clip = this.gameState.attemptClips[this.currentPlayAllIndex];
            shouldReverse = true;
            logMessage = `Playing attempt ${this.currentPlayAllIndex + 1} in loop sequence`;
        }
        
        try {
            // Resume audio context if needed
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            // Decode the clip
            const response = await fetch(clip.data);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            // Reverse buffer if needed
            const finalBuffer = shouldReverse ? this.reverseAudioBuffer(audioBuffer) : audioBuffer;
            
            const source = this.audioContext.createBufferSource();
            source.buffer = finalBuffer;
            source.connect(this.audioContext.destination);
            
            source.onended = () => {
                if (this.isPlayingAll) {
                    this.currentPlayAllIndex++;
                    // Configured pause before next clip
                    this.playAllTimeout = setTimeout(() => {
                        this.playNextInSequence();
                    }, GAME_CONFIG.DELAYS.PLAY_ALL);
                }
            };
            
            source.start(0);
            console.log(logMessage);
            
        } catch (error) {
            console.error('Error in play all sequence:', error);
            this.stopPlayAll();
        }
    }

    /**
     * Stop the play-all sequence
     */
    stopPlayAll() {
        this.isPlayingAll = false;
        this.currentPlayAllIndex = 0;
        this.playAllButton.textContent = '▶️ Play All';
        
        if (this.playAllTimeout) {
            clearTimeout(this.playAllTimeout);
            this.playAllTimeout = null;
        }
        
        // Stop any currently playing audio
        this.stopAllGameClipPlayback();
        
        console.log('Play all sequence stopped');
    }

    /**
     * Reverse an audio buffer
     * Creates a new buffer with the audio samples in reverse order
     */
    reverseAudioBuffer(audioBuffer) {
        const reversedBuffer = this.audioContext.createBuffer(
            audioBuffer.numberOfChannels,
            audioBuffer.length,
            audioBuffer.sampleRate
        );
        
        for (let channel = 0; channel < audioBuffer.numberOfChannels; channel++) {
            const originalData = audioBuffer.getChannelData(channel);
            const reversedData = reversedBuffer.getChannelData(channel);
            
            for (let i = 0; i < originalData.length; i++) {
                reversedData[i] = originalData[originalData.length - 1 - i];
            }
        }
        
        console.log('Audio buffer reversed successfully');
        return reversedBuffer;
    }
}

// Initialize game controller when page loads
let gameController;
document.addEventListener('DOMContentLoaded', async () => {
    // Only initialize on game page
    if (document.getElementById('gameClipsList')) {
        // Check for microphone permissions first
        const statusElement = document.getElementById('status');
        if (statusElement) {
            const permission = await MicrophonePermissions.ensurePermission(statusElement);
            console.log('Game page microphone permission status:', permission);
            
            // If permission denied, disable recording functionality
            if (permission === 'denied') {
                const recordButton = document.getElementById('recordButton');
                if (recordButton) {
                    recordButton.disabled = true;
                }
                return; // Don't initialize game controller
            }
        }
        
        console.log('Initializing game controller...');
        gameController = new GameController();
    }
});
