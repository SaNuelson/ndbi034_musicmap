$(()=>{
    $('#uploadBtn').on('click', function() {
        console.log("CLIKC");
        setTimeout(()=>$('#uploadInput').trigger('click'),10);
    })
})