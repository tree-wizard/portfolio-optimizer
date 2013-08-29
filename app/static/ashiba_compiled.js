/* Compiled with Ashiba v0.0 */

$(window).load(function(){
  $("#calculate").on("click",
    ashiba.eventHandlerFactory("calculate", "click")
  );
});