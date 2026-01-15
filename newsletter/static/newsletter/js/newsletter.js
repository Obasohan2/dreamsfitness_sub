document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("newsletterModal");

    if (modalEl && typeof $ !== "undefined") {
        $(modalEl).modal({
            backdrop: 'static',
            keyboard: true,
            show: true
        });
    }
});






// document.addEventListener("DOMContentLoaded", function () {
//     const modal = document.getElementById("newsletterModal");

//     if (modal && typeof $ !== "undefined") {
//         $('#newsletterModal').modal('show');
//     }
// });





// document.addEventListener("DOMContentLoaded", function () {
//     const modal = document.getElementById("newsletterModal");

//     if (modal && typeof $ !== "undefined") {
//         $('#newsletterModal').modal('show');
//     }
// });
