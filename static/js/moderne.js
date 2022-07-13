var Retro = {

    seconds_clock: function () {

        // one second intervals
        function clock () {
            var now = new Date()
            var h = now.getHours()
            var m = now.getMinutes()
            var s = now.getSeconds()

            document.getElementById("date").innerHTML = h + ":" + m + ":" + s
            setTimeout(function() { clock() }, 1000)
        }

        clock()
    },

    recv_json: function (json) {
        console.log(json)

        const { id, value } = json
        document.getElementById(id).innerHTML = value
    },

    ui: function () {
        document.getElementById('toggle').onclick =
            () => { socket.emit('json', {webapp: 'toggle-button'})}
    },
    
    init: function () {
        this.ui()
        this.seconds_clock()
    }
}
