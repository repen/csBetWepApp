
var arr = [...document.querySelectorAll("a:not(.nav-link)")].filter(el=>{

    if ((el.childNodes[1].innerText.split(" ").length > 3)) {
        return true;
    } else {
        el.remove();
    }


});

arr.sort(function (a,b) {
    var date = a.childNodes[1].innerText.split("\n");
    var a_datestring = "";
    if (date[1] !== undefined) {
        date[1] = date[1].replace(/\./g, '-');
        a_datestring = `${date[1].split(" ")[0]}T${date[1].split(" ")[1]}:00.000Z`;
        var a_msUTC = Date.parse(a_datestring);
    }

    date = b.childNodes[1].innerText.split("\n");
    var b_datestring = "";
    if (date[1] !== undefined) {
        date[1] = date[1].replace(/\./g, '-');
        b_datestring = `${date[1].split(" ")[0]}T${date[1].split(" ")[1]}:00.000Z`;
        var b_msUTC = Date.parse(b_datestring);
    }

    return a_msUTC < b_msUTC;
});

var container = document.querySelector(".container");
container.innerHTML = "";

arr.forEach(function (el, index) {

    var date = el.childNodes[1].innerText.split(" ");
    var datestring = "";
    date = date.slice(-2, -1) + " " + date.slice(-1);
    date = date.replace(/\./g, '-');
    datestring = `${date.split(" ")[0]}T${date.split(" ")[1]}:00.000Z`;
    var msUTC = Date.parse(datestring);
    if (msUTC + 7*60*60*1000 < Date.now()) {
        el.childNodes[1].classList.remove("btn-light");
        el.childNodes[1].classList.add("btn-info");
    }

    container.innerHTML += el.outerHTML;
});


container.innerHTML = '<p>Date: <input type="text" id="datepicker"></p>' + container.innerHTML;



(function() {

    $( "#datepicker" ).datepicker({
        onSelect  : function(Text){
            // console.log(el);
            window.location.href = "/?date=" + Text;
        }
    });

})();