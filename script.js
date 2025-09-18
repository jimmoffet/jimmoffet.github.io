class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.audioContext = null;
    this.chunks = [];
    this.isRecording = false;
    this.clipDurations = {}; // Store durations for each clip ID
    this.currentSource = null;
    this.isPlaying = false;
    this.isPaused = false;
    this.currentClipId = null;
    this.isReversed = false;
    this.startTime = 0;
    this.pausedAt = 0;
    this.duration = 0;
    this.timeUpdateInterval = null;
    this.currentAudioBuffer = null; // Store the current audio buffer for resume
    this.lastLogSecond = 0; // For throttling debug logs

    // Game playback state for history page
    this.isPlayingAll = false;
    this.currentGameId = null;
    this.currentPlayAllIndex = 0;
    this.gameClips = null;
    this.playAllTimeout = null;

    this.recordButton = document.getElementById("recordButton");
    this.status = document.getElementById("status");
    this.clipsList = document.getElementById("clipsList");
    this.clearAllButton = document.getElementById("clearAll");

    this.init();
    console.log(
      "AudioRecorder initialized. Clips in storage:",
      StorageService.getAllClips().length
    );
  }

  async init() {
    try {
      // Initialize audio context
      this.audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      console.log("AudioContext created:", this.audioContext.state);

      this.setupEventListeners();
      this.renderClips();

      // Load durations for existing clips
      this.loadClipDurations();
    } catch (error) {
      console.error("Failed to initialize audio recorder:", error);
      if (this.status)
        this.status.textContent = "Failed to initialize audio system";
      if (this.recordButton) this.recordButton.disabled = true;
    }
  }

  setupEventListeners() {
    if (this.recordButton) {
      this.recordButton.addEventListener("click", () => this.toggleRecording());
    }
    if (this.clearAllButton) {
      this.clearAllButton.addEventListener("click", () => this.clearAllClips());
    }
    console.log("Event listeners set up");
  }

  async loadClipDurations() {
    const clips = StorageService.getAllClips();
    console.log("Loading durations for", clips.length, "clips...");

    for (const clip of clips) {
      try {
        // Skip if we already have the duration
        if (this.clipDurations[clip.id]) continue;

        // Convert base64 to arrayBuffer and decode
        const response = await fetch(clip.data);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer =
          await this.audioContext.decodeAudioData(arrayBuffer);

        this.clipDurations[clip.id] = audioBuffer.duration;
        console.log(
          `Loaded duration for clip ${clip.id}: ${audioBuffer.duration.toFixed(2)}s`
        );

        // Update the specific clip's time display
        this.updateClipTimeDisplay(clip.id, 0, audioBuffer.duration);
      } catch (error) {
        console.error(`Failed to load duration for clip ${clip.id}:`, error);
        // Set a fallback duration
        this.clipDurations[clip.id] = 0;
      }
    }

    console.log("Clip durations loaded:", this.clipDurations);
  }

  async loadClipDuration(clipId) {
    const clips = StorageService.getAllClips();
    const clip = clips.find((c) => c.id === clipId);
    if (!clip) return;

    try {
      const response = await fetch(clip.data);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

      this.clipDurations[clipId] = audioBuffer.duration;
      console.log(
        `Loaded duration for new clip ${clipId}: ${audioBuffer.duration.toFixed(2)}s`
      );

      // Update the time display
      this.updateClipTimeDisplay(clipId, 0, audioBuffer.duration);
    } catch (error) {
      console.error(`Failed to load duration for new clip ${clipId}:`, error);
      this.clipDurations[clipId] = 0;
    }
  }

  updateClipTimeDisplay(clipId, currentTime = 0, totalTime = null) {
    const timeElement = document.getElementById(`time-${clipId}`);
    if (timeElement) {
      const duration = totalTime || this.clipDurations[clipId] || 0;
      timeElement.textContent = `${this.formatTime(currentTime)} / ${this.formatTime(duration)}`;
    }
  }

  async toggleRecording() {
    if (this.isRecording) {
      this.stopRecording();
    } else {
      await this.startRecording();
    }
  }

  async startRecording() {
    try {
      console.log("Starting recording...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      this.mediaRecorder = new MediaRecorder(stream);
      this.chunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        console.log("Audio data chunk received:", event.data.size, "bytes");
        this.chunks.push(event.data);
      };

      this.mediaRecorder.onstart = () => {
        console.log("MediaRecorder onstart event fired - recording began");
        if (this.status)
          this.status.textContent = "🔴 Recording... Click to stop";
      };

      this.mediaRecorder.onstop = () => {
        console.log("Recording stopped, processing audio...");
        this.processRecording();
        stream.getTracks().forEach((track) => track.stop());
      };

      console.log("Calling mediaRecorder.start()");
      this.mediaRecorder.start();
      this.isRecording = true;

      // Update UI immediately
      if (this.recordButton) {
        this.recordButton.classList.add("recording");
        this.recordButton.textContent = "⏹️";
      }
      if (this.status) this.status.textContent = "Starting recording...";
    } catch (error) {
      console.error("Failed to start recording:", error);
      if (this.status) this.status.textContent = "Failed to start recording";
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      console.log("Stopping recording...");
      this.mediaRecorder.stop();
      this.isRecording = false;

      if (this.recordButton) {
        this.recordButton.classList.remove("recording");
        this.recordButton.textContent = "🎤";
      }
      if (this.status) this.status.textContent = "Processing recording...";
    }
  }

  async processRecording() {
    try {
      const blob = new Blob(this.chunks, { type: "audio/webm" });
      console.log("Created audio blob:", blob.size, "bytes, type:", blob.type);

      // Convert to base64 for localStorage
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Data = reader.result;
        const recordingStartTime = Date.now();

        // Create regular clip using metadata factory
        const clip = ClipMetadata.createRegular(recordingStartTime, base64Data);

        // Save using centralized storage service
        StorageService.saveClip(clip);

        console.log(
          "Clip saved to localStorage. Total clips:",
          StorageService.getAllClips().length
        );
        console.log("Clip details:", {
          id: clip.id,
          size: clip.size,
          timestamp: clip.timestamp,
        });

        // Load the duration for the new clip
        this.loadClipDuration(clip.id);

        this.renderClips();
        if (this.status)
          this.status.textContent = "Recording saved! Click to record again";
      };

      reader.readAsDataURL(blob);
    } catch (error) {
      console.error("Failed to process recording:", error);
      if (this.status) this.status.textContent = "Failed to save recording";
    }
  }

  async playClip(clipId, reverse = false) {
    try {
      console.log(`Playing clip ${clipId}, reverse: ${reverse}`);

      const clips = StorageService.getAllClips();
      const clip = clips.find((c) => c.id === clipId);
      if (!clip) {
        console.error("Clip not found:", clipId);
        return;
      }

      // Resume audio context if needed
      if (this.audioContext.state === "suspended") {
        await this.audioContext.resume();
        console.log("AudioContext resumed");
      }

      // Stop any currently playing audio
      this.stopPlayback();

      // Convert base64 back to blob and decode
      const response = await fetch(clip.data);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      console.log("Audio decoded. Duration:", audioBuffer.duration, "seconds");

      // Store the audio buffer for potential resume
      this.currentAudioBuffer = audioBuffer;

      // Set up playback state
      console.log("=== PLAY DEBUG ===");
      console.log("Starting new playback for clip:", clipId);
      console.log("Reverse mode:", reverse);
      console.log("Audio duration:", audioBuffer.duration);
      console.log("Current audio context time:", this.audioContext.currentTime);

      this.currentClipId = clipId;
      this.isReversed = reverse;
      this.duration = audioBuffer.duration;
      this.isPlaying = true;
      this.isPaused = false;
      this.startTime = this.audioContext.currentTime;
      this.pausedAt = 0;

      console.log("Set startTime to:", this.startTime);
      console.log("Reset pausedAt to:", this.pausedAt);
      console.log("==================");

      // Create source and connect to destination
      const source = this.audioContext.createBufferSource();

      if (reverse) {
        source.buffer = this.reverseAudioBuffer(audioBuffer);
        console.log("Playing in reverse");
      } else {
        source.buffer = audioBuffer;
      }

      source.connect(this.audioContext.destination);
      this.currentSource = source;

      source.onended = () => {
        console.log("Playback completed");
        this.stopPlayback();
      };

      source.start(0);
      console.log("Playback started");

      // Start time updates and update UI
      this.startTimeUpdates();
      this.updateClipUI(clipId);
    } catch (error) {
      console.error("Failed to play clip:", error);
    }
  }

  pausePlayback() {
    if (this.isPlaying && !this.isPaused && this.currentSource) {
      console.log("=== PAUSE DEBUG ===");
      console.log("Current audio context time:", this.audioContext.currentTime);
      console.log("Playback start time:", this.startTime);
      console.log(
        "Calculated elapsed time:",
        this.audioContext.currentTime - this.startTime
      );

      this.pausedAt = this.audioContext.currentTime - this.startTime;
      console.log("Setting pausedAt to:", this.pausedAt);
      console.log("Duration:", this.duration);
      console.log("Remaining time would be:", this.duration - this.pausedAt);

      // Remove the onended handler to prevent it from calling stopPlayback
      this.currentSource.onended = null;
      this.currentSource.stop();
      this.currentSource = null;
      this.isPlaying = false;
      this.isPaused = true;

      console.log(
        "State after pause - isPlaying:",
        this.isPlaying,
        "isPaused:",
        this.isPaused
      );
      console.log("Removed onended handler to prevent auto-stop");
      console.log("==================");

      this.stopTimeUpdates();
      this.updateClipUI(this.currentClipId);
    }
  }

  async resumePlayback() {
    if (this.isPaused && this.currentClipId && this.currentAudioBuffer) {
      console.log("=== RESUME DEBUG ===");
      console.log(
        "Attempting to resume from pausedAt:",
        this.pausedAt,
        "seconds"
      );
      console.log("Current clip ID:", this.currentClipId);
      console.log("Is reversed:", this.isReversed);
      console.log("Total duration:", this.duration);
      console.log("Has audio buffer:", !!this.currentAudioBuffer);
      console.log(
        "Current state - isPaused:",
        this.isPaused,
        "isPlaying:",
        this.isPlaying
      );

      // Create new source using stored audio buffer
      const source = this.audioContext.createBufferSource();

      if (this.isReversed) {
        source.buffer = this.reverseAudioBuffer(this.currentAudioBuffer);
        console.log("Using reversed buffer");
      } else {
        source.buffer = this.currentAudioBuffer;
        console.log("Using normal buffer");
      }

      source.connect(this.audioContext.destination);
      this.currentSource = source;

      source.onended = () => {
        console.log("Playback completed from resume");
        this.stopPlayback();
      };

      // Calculate remaining duration
      const remainingDuration = this.duration - this.pausedAt;
      console.log("Calculated remaining duration:", remainingDuration);

      // Start from paused position
      console.log(
        "Calling source.start(0,",
        this.pausedAt,
        ",",
        remainingDuration,
        ")"
      );
      source.start(0, this.pausedAt, remainingDuration);

      // Adjust start time to account for elapsed time
      const newStartTime = this.audioContext.currentTime - this.pausedAt;
      console.log("Current audio context time:", this.audioContext.currentTime);
      console.log("Setting new start time to:", newStartTime);
      console.log(
        "This should make elapsed time calculation start at:",
        this.pausedAt
      );

      this.startTime = newStartTime;
      this.isPlaying = true;
      this.isPaused = false;

      console.log(
        "State after resume - isPlaying:",
        this.isPlaying,
        "isPaused:",
        this.isPaused
      );
      console.log("==================");

      this.startTimeUpdates();
      this.updateClipUI(this.currentClipId);
    }
  }

  stopPlayback() {
    if (this.currentSource) {
      this.currentSource.stop();
      this.currentSource = null;
    }
    this.isPlaying = false;
    this.isPaused = false;
    this.currentClipId = null;
    this.isReversed = false;
    this.pausedAt = 0;
    this.currentAudioBuffer = null; // Clear stored buffer
    this.stopTimeUpdates();

    // Only re-render if we're not in a game play all sequence
    // (to avoid resetting button states during game playback)
    if (!this.isPlayingAll) {
      this.renderClips(); // Refresh all clip UIs
    }
  }

  startTimeUpdates() {
    this.stopTimeUpdates();
    this.timeUpdateInterval = setInterval(() => {
      this.updateTimeDisplay();
    }, 100);
  }

  stopTimeUpdates() {
    if (this.timeUpdateInterval) {
      clearInterval(this.timeUpdateInterval);
      this.timeUpdateInterval = null;
    }
  }

  updateTimeDisplay() {
    if (!this.isPlaying || !this.currentClipId) return;

    const elapsed = this.audioContext.currentTime - this.startTime;
    const timeElement = document.getElementById(`time-${this.currentClipId}`);

    // Debug every 10th update (once per second at 100ms intervals)
    if (Math.floor(Date.now() / 1000) !== this.lastLogSecond) {
      this.lastLogSecond = Math.floor(Date.now() / 1000);
      console.log(
        "Time update - AudioContext time:",
        this.audioContext.currentTime,
        "Start time:",
        this.startTime,
        "Elapsed:",
        elapsed
      );
    }

    if (timeElement) {
      let currentTime, totalTime;

      if (this.isReversed) {
        // For reverse playback, show countdown
        currentTime = Math.max(0, this.duration - elapsed);
        totalTime = this.duration;
      } else {
        // For normal playbook, show elapsed
        currentTime = Math.min(elapsed, this.duration);
        totalTime = this.duration;
      }

      timeElement.textContent = `${this.formatTime(currentTime)} / ${this.formatTime(totalTime)}`;
    }
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }

  updateClipUI(clipId) {
    // Update all clip controls to reflect current state
    this.renderClips();
  }

  reverseAudioBuffer(audioBuffer) {
    console.log("Reversing audio buffer...");

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

    console.log("Audio buffer reversed successfully");
    return reversedBuffer;
  }

  toggleClipInfo(infoId) {
    const infoElement = document.getElementById(infoId);
    if (infoElement) {
      infoElement.style.display =
        infoElement.style.display === "none" ? "block" : "none";
    }
  }

  deleteClip(clipId) {
    console.log("Deleting clip:", clipId);
    StorageService.deleteClips([clipId]);
    console.log(
      "Clip deleted. Remaining clips:",
      StorageService.getAllClips().length
    );
    this.renderClips();
  }

  clearAllClips() {
    if (confirm("Are you sure you want to delete all recordings?")) {
      console.log("Clearing all clips...");
      StorageService.clearAllClips();
      console.log("All clips cleared");
      this.renderClips();
    }
  }

  formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  }

  formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return Math.round(bytes / 1024) + " KB";
    return Math.round(bytes / 1048576) + " MB";
  }

  renderClips() {
    const clips = StorageService.getAllClips();
    console.log("Rendering clips. Total:", clips.length);

    if (clips.length === 0) {
      this.clipsList.innerHTML =
        '<div class="no-clips">No recordings yet. Click the 🍌 to play the game!</div>';
      this.clearAllButton.style.display = "none";
      return;
    }

    this.clearAllButton.style.display = "block";

    // Group clips by game session
    const gameGroups = this.groupClipsByGame();

    this.clipsList.innerHTML = gameGroups
      .map((gameGroup, gameIndex) => {
        const gameLabel = this.formatGameLabel(gameGroup.gameStartTime);
        const gameId = `game-${gameGroup.gameStartTime}`;
        const clipCount = gameGroup.clips.length;
        const targetClip =
          gameGroup.clips.find((clip) => clip.clipType === "target") ||
          gameGroup.clips[0];
        const attemptClips =
          gameGroup.clips.filter((clip) => clip.clipType === "attempt") ||
          gameGroup.clips.slice(1);

        const isCurrentGame = this.currentGameId === gameId;
        const isPlayingAll = isCurrentGame && this.isPlayingAll;

        return `
            <div class="game-group" data-game-id="${gameId}">
                <div class="game-label">${gameLabel}</div>
                <div class="game-summary">
                    <span class="clip-count">${attemptClips.length > 0 ? `${attemptClips.length} copycat${attemptClips.length !== 1 ? "s" : ""} 😻` : "no copycats 👎"}</span>
                    <div class="game-controls">
                        <button class="play-all-button ${isPlayingAll ? "playing" : ""}" 
                                onclick="recorder.toggleGamePlayAll('${gameId}')"
                                data-game-id="${gameId}">
                            ${isPlayingAll ? "⏹️ Stop" : "▶️ Listen"}
                        </button>
                        <button class="delete-game-button" 
                                onclick="recorder.deleteGame('${gameId}')" 
                                title="Delete entire game">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
            `;
      })
      .join("");

    console.log("Clips rendered successfully");
  }

  /**
   * Toggle play all for a specific game
   */
  toggleGamePlayAll(gameId) {
    if (this.currentGameId === gameId && this.isPlayingAll) {
      this.stopGamePlayAll();
    } else {
      this.startGamePlayAll(gameId);
    }
  }

  /**
   * Start playing all clips in a game
   */
  async startGamePlayAll(gameId) {
    // Stop any current playback
    this.stopPlayback();
    this.stopGamePlayAll();

    // Find the game clips
    const gameGroups = this.groupClipsByGame();
    const gameGroup = gameGroups.find(
      (group) => `game-${group.gameStartTime}` === gameId
    );

    if (!gameGroup || !gameGroup.clips.length) {
      console.error("Game not found or no clips:", gameId);
      return;
    }

    // Set up game playback state
    this.currentGameId = gameId;
    this.isPlayingAll = true;
    this.currentPlayAllIndex = -1; // Start with -1 to play target first
    this.gameClips = gameGroup.clips;

    // Sort clips: target first, then attempts by index
    this.gameClips.sort((a, b) => {
      if (a.clipType === "target") return -1;
      if (b.clipType === "target") return 1;
      return (a.gameClipIndex || 0) - (b.gameClipIndex || 0);
    });

    console.log(
      "Starting game play all for:",
      gameId,
      "clips:",
      this.gameClips.length
    );

    // Update UI
    this.updatePlayAllButton(gameId, true);

    // Start playback sequence
    this.playNextGameClip();
  }

  /**
   * Play the next clip in the current game sequence
   */
  async playNextGameClip() {
    if (!this.isPlayingAll || !this.gameClips) {
      return;
    }

    // Check if we've reached the end and should loop back
    if (this.currentPlayAllIndex >= this.gameClips.length - 1) {
      console.log("Looping back to start of game play-all sequence");
      this.currentPlayAllIndex = -1; // Reset to play target first
    }

    this.currentPlayAllIndex++;
    const clip = this.gameClips[this.currentPlayAllIndex];

    if (!clip) {
      console.error("No clip found at index:", this.currentPlayAllIndex);
      this.stopGamePlayAll();
      return;
    }

    // Determine if this clip should be played in reverse
    const shouldReverse = clip.clipType !== "target"; // Reverse attempts, normal for target
    const logMessage =
      clip.clipType === "target"
        ? "Playing target clip in game sequence"
        : `Playing attempt ${clip.gameClipIndex || this.currentPlayAllIndex} in game sequence`;

    try {
      // Resume audio context if needed
      if (this.audioContext.state === "suspended") {
        await this.audioContext.resume();
      }

      // Decode the clip
      const response = await fetch(clip.data);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

      // Reverse buffer if needed
      const finalBuffer = shouldReverse
        ? this.reverseAudioBuffer(audioBuffer)
        : audioBuffer;

      const source = this.audioContext.createBufferSource();
      source.buffer = finalBuffer;
      source.connect(this.audioContext.destination);

      this.currentSource = source;
      this.currentClipId = clip.id;
      this.isPlaying = true;

      source.onended = () => {
        this.currentSource = null;
        this.isPlaying = false;

        if (this.isPlayingAll) {
          // Continue with next clip after a pause
          this.playAllTimeout = setTimeout(() => {
            this.playNextGameClip();
          }, 1000); // 1 second pause between clips
        }
      };

      source.start(0);
      console.log(logMessage);
    } catch (error) {
      console.error("Error in game play all sequence:", error);
      this.stopGamePlayAll();
    }
  }

  /**
   * Stop game play all sequence
   */
  stopGamePlayAll() {
    if (!this.isPlayingAll) return;

    this.isPlayingAll = false;
    const gameId = this.currentGameId;

    this.currentGameId = null;
    this.currentPlayAllIndex = 0;
    this.gameClips = null;

    // Clear timeout
    if (this.playAllTimeout) {
      clearTimeout(this.playAllTimeout);
      this.playAllTimeout = null;
    }

    // Stop any current audio without re-rendering (to preserve button state)
    if (this.currentSource) {
      this.currentSource.stop();
      this.currentSource = null;
    }
    this.isPlaying = false;
    this.isPaused = false;
    this.currentClipId = null;
    this.stopTimeUpdates();

    // Update UI
    if (gameId) {
      this.updatePlayAllButton(gameId, false);
    }

    console.log("Game play all sequence stopped");
  }

  /**
   * Update the play all button UI for a specific game
   */
  updatePlayAllButton(gameId, isPlaying) {
    const button = document.querySelector(
      `.play-all-button[data-game-id="${gameId}"]`
    );
    if (button) {
      button.textContent = isPlaying ? "⏹️ Stop" : "▶️ Listen";
      button.classList.toggle("playing", isPlaying);
    } else {
      console.warn("Play all button not found for game:", gameId);
    }
  }

  /**
   * Delete an entire game (all clips belonging to a game session)
   */
  deleteGame(gameId) {
    if (!confirm("Delete this entire game? This cannot be undone.")) {
      return;
    }

    // Stop any playback for this game
    if (this.currentGameId === gameId) {
      this.stopGamePlayAll();
    }

    // Extract gameStartTime from gameId (format: "game-1234567890")
    const gameStartTime = parseInt(gameId.replace("game-", ""));

    // Delete through StorageService
    const deletedCount = StorageService.deleteGameByStartTime(gameStartTime);

    console.log("Deleted game:", gameId, "clips removed:", deletedCount);

    // Re-render clips (this will fetch fresh data from StorageService)
    this.renderClips();
  }

  groupClipsByGame() {
    // Group clips by gameStartTime, fallback to individual clips if no game metadata
    const games = {};
    const clips = StorageService.getAllClips();

    clips.forEach((clip) => {
      const gameKey = clip.gameStartTime || clip.timestamp; // Fallback for old clips
      if (!games[gameKey]) {
        games[gameKey] = {
          gameStartTime: gameKey,
          clips: [],
        };
      }
      games[gameKey].clips.push(clip);
    });

    // Sort games by start time (newest first) and clips within each game
    return Object.values(games)
      .sort((a, b) => b.gameStartTime - a.gameStartTime)
      .map((game) => ({
        ...game,
        clips: game.clips.sort((a, b) => {
          // Sort by gameClipIndex if available, otherwise by timestamp
          if (a.gameClipIndex !== undefined && b.gameClipIndex !== undefined) {
            return a.gameClipIndex - b.gameClipIndex;
          }
          return a.timestamp - b.timestamp;
        }),
      }));
  }

  formatGameLabel(timestamp) {
    const now = Date.now();
    const gameTime = new Date(timestamp);
    const diffMs = now - timestamp;
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 60) {
      // Less than an hour ago
      return `Game played ${diffMinutes} minute${diffMinutes !== 1 ? "s" : ""} ago`;
    } else if (diffHours < 24) {
      // Less than a day ago
      return `Game played ${diffHours} hour${diffHours !== 1 ? "s" : ""} ago`;
    } else if (diffDays === 1) {
      return "Game played yesterday";
    } else {
      return `Game ${diffDays} days ago`;
    }
  }

  /**
   * Reverse an audio buffer (same as in game.js)
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

    console.log("Audio buffer reversed successfully");
    return reversedBuffer;
  }
}

// Initialize the recorder when the page loads
let recorder;
document.addEventListener("DOMContentLoaded", async () => {
  // Only initialize AudioRecorder on pages that have the clipsList element (history page)
  if (document.getElementById("clipsList")) {
    console.log("DOM loaded, initializing AudioRecorder for history page...");
    recorder = new AudioRecorder();
  }
});

// Debug function to check localStorage
function debugStorage() {
  const clips = JSON.parse(localStorage.getItem("hearsayClips") || "[]");
  console.log("Storage debug - Total clips:", clips.length);
  clips.forEach((clip, index) => {
    console.log(`Clip ${index + 1}:`, {
      id: clip.id,
      timestamp: clip.timestamp,
      size: clip.size,
      dataLength: clip.data ? clip.data.length : 0,
    });
  });
}

// Debug function to test audio capabilities
function debugAudio() {
  console.log("=== Audio Debug Info ===");
  console.log(
    "AudioContext support:",
    !!(window.AudioContext || window.webkitAudioContext)
  );
  console.log("MediaRecorder support:", !!window.MediaRecorder);
  console.log(
    "getUserMedia support:",
    !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  );

  if (recorder) {
    console.log("AudioContext state:", recorder.audioContext?.state);
    console.log("AudioContext sample rate:", recorder.audioContext?.sampleRate);
    console.log("Current clips count:", recorder.clips.length);

    // Test audio context with a simple tone
    if (recorder.audioContext && recorder.audioContext.state === "running") {
      console.log("Testing audio output with 440Hz tone...");
      const oscillator = recorder.audioContext.createOscillator();
      const gainNode = recorder.audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(recorder.audioContext.destination);

      oscillator.frequency.value = 440;
      gainNode.gain.setValueAtTime(0.1, recorder.audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        recorder.audioContext.currentTime + 0.5
      );

      oscillator.start(recorder.audioContext.currentTime);
      oscillator.stop(recorder.audioContext.currentTime + 0.5);

      console.log("Tone test initiated - you should hear a brief beep");
    }
  }
}

// Make debug functions available globally for testing
window.debugStorage = debugStorage;
window.debugAudio = debugAudio;

// Log when audio context state changes
document.addEventListener("click", () => {
  if (recorder && recorder.audioContext) {
    console.log(
      "AudioContext state after user interaction:",
      recorder.audioContext.state
    );
  }
});
