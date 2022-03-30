class AudioPlayer {

    duration_sec = 0
    current_play_sec = 0
    trackIndex = 0
    myTrack = null
    audioElement = null
    songStarted = false
    songList = null
    space_grap = "   *"
    plotted = false
    previous_index = 0
    currentVolume = 0.5;

    constructor(myTrack) {

        this.myTrack = myTrack
        this.audioElement = document.getElementById("myplayer")

        this.loadSongMenu()
        this.loadMenuColor()
        this.trackAction()
        this.changeColor(this.trackIndex)
    }

    loadSongMenu() {
        this.songList = document.getElementById("list-menu").children[0]
        for (let i = 0; i < this.myTrack.length; i++) {
           this.songList.innerHTML += `<li class=\"list-group-item\"><a id=${i}>${myTrack[i].split(".")[0]}</a></li>`
           
        }
        this.songList.innerHTML += `
            <li class=\"list-group-item\" data-bs-toggle="modal" data-bs-target="#staticBackdrop"><a id="upload_link">Add New Song</a></li>
        `
    }

    changeVolume(value) {
        this.currentVolume = value/100
        this.audioElement.volume = this.currentVolume

        if (this.audioElement.volume == 0) {
            document.getElementById("myvolume").setAttribute("class", "fas fa-volume-mute")
        } else {
            document.getElementById("myvolume").setAttribute("class", "fas fa-volume-up")   
        }
    }

    displayTime() {
        document.getElementById("time_slider").value = parseInt((this.audioElement.currentTime/this.audioElement.duration) * 100)
    }

    displaySongInfo() {
        document.getElementById("currentTitle").innerHTML = this.myTrack[this.trackIndex].split(".")[0].slice(0, 35) + 
            this.space_grap +  " " + this.displayCurrentPlayTime()
    }

    displayCurrentPlayTime(){
        return parseInt(this.current_play_sec /60) + 
            ":" + 
            String(parseInt(this.current_play_sec % 60)).padStart(2, "0")  + 
            " / " + this.duration_sec
    }
    loadSong() {
        if (!((this.trackIndex >= this.myTrack.length))) {
            this.songStarted = true 

            this.audioElement.src = "/my_song_folder/" + this.myTrack[this.trackIndex]
            this.audioElement.volume = this.currentVolume

            this.audioElement.play()
            this.changeColor(this.trackIndex)
            
            this.audioElement.onloadedmetadata = (event) => {
                this.duration_sec = this.audioElement.duration
                this.duration_sec = parseInt(this.duration_sec / 60) + ":" + String(parseInt(this.duration_sec % 60)).padStart(2, "0")
            }
            
            this.audioElement.ontimeupdate = (event) => {
                this.current_play_sec = this.audioElement.currentTime

                if (parseInt(this.current_play_sec) % 45 == 0) {

                    if (!this.plotted) {
                        this.space_grap += "*"
                        this.plotted = !this.plotted
                    }
                       
                } else {
                    if(this.plotted) {
                        this.plotted = false
                    }
                }
               
                this.displaySongInfo()
                /**this.songList.children[this.trackIndex].children[0].innerHTML = currentTitle + " " + 
                    "<span style='text-align:right'>" + this.displayCurrentPlayTime() + "</span>"
                **/
            }
            
            this.audioElement.onended = (event) => {
                if (this.trackIndex < this.myTrack.length) {
                    //this.songStarted = false
                    this.space_grap = "   *"
                    this.playNext()
                }
            }
        } else if (this.trackIndex < -1) {
            this.resetJuke()
            this.loadSong()
        }
    }

    changeTrack(trackNumber) {
        this.songStarted = false

        if (trackNumber < this.myTrack.length) {
            this.trackIndex = trackNumber
        }
    }

    resetJuke() {
        this.trackIndex = 0
        this.space_grap = "   *"
        this.songStarted = false
    }

    playSong() {
        if (this.songStarted) {
            this.pauseSong()

        } else {
            this.loadSong()
        }
    }

    muteSound() {
        this.audioElement.muted = !this.audioElement.muted
    }

    playNext() {
        if (this.trackIndex >= this.myTrack.length - 1) {
            document.getElementById("currentTitle").innerHTML = "You are at Last Track"
            //this.trackIndex = 0

        } else {
            this.trackIndex++
            this.songStarted= false
            this.playSong()

        }
        //this.songStarted= false
        this.space_grap = "   *"
    }

    playPrevious() {
        if (this.trackIndex <= 0) {
            document.getElementById("currentTitle").innerHTML = "You are at the First Track"
            //this.trackIndex = 0

        } else {
            this.trackIndex--
            this.songStarted = false
            this.playSong()

        }
        this.space_grap = "   *"
    }

    pauseSong() {
        if (!this.audioElement.paused) {
            document.getElementById("playButton").children[0].setAttribute("class", "far fa-pause-circle")
            this.audioElement.pause()

        } else {
            document.getElementById("playButton").children[0].setAttribute("class", "far fa-play-circle")
            this.audioElement.play()
        }
    }
    
    loadMenuColor() {
        for (let i = 0; i < this.songList.children.length; i++) {
            this.songList.children[i].style.backgroundColor = "\#FCF3CF"
            this.songList.children[i].style.color = "black"
        }
    }

    changeColor(index) {
        if (index < this.songList.children.length) {
            this.songList.children[index].style.backgroundColor = "\#D35400"
            this.songList.children[index].style.color = "white"

            if (this.previous_index != index) {
                this.songList.children[this.previous_index].style.backgroundColor = "\#FCF3CF"
                this.songList.children[this.previous_index].style.color = "black"
            }

            this.previous_index = index
            
        }
    }

    trackAction() {
        let songMenu = document.getElementsByTagName("li")
        for (let i = 0; i < songMenu.length - 1; i++) {
            songMenu[i].onclick = (event) => {
                this.changeTrack(i)
                this.playSong()
                this.space_grap = "   *"
            }
        }
    }
}