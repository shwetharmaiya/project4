function updatelike(ele){
    //update like
console.log("HELLO")  
 post_id = ele.value
 console.log(post_id)
 fetch(`like/${post_id}`)
 .then(response => response.text())
 .then(text => {

     result = JSON.parse(text)
     element = ele.querySelector(".fa-heart")
 
     id = `#num_likes_${post_id}`

     if (result["type"] === "add"){
         
         //red if post is liked by user
         element.style.color = "#f7786b";
         
     }
     if (result["type"] === "remove"){
          //white if post not liked by other user
         element.style.color = "#f0efef"
         
     }
     
     document.querySelector(id).innerHTML=result["num_of_likes"] +" like(s)"

 })
     
 
     
}
function likefeature(){
    console.log("THAT 1")
    //call updatelike whenever like button is click
    document.querySelectorAll("#like").forEach( e=> {
        
        e.onclick = function(){
            console.log("THAT")
            updatelike(this)
        }
    });
}

document.addEventListener('DOMContentLoaded',function(){
    // call likefeature function when page is loaded 
    console.log("THIS")
           
    likefeature();
    console.log("THIS 1")
});
