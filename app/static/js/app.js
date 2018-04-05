// // register modal component
// Vue.component('modal', {
//   template: '#modal-template'
// })
Vue.filter('fromNow',function(date){
  return moment(date).fromNow(true)
});

var vm = new Vue({
  el: '#vueEl',
  // delimiters: ["[[", "]]"],
  data: {
    isActiveModal:false,
    formFollow: "",
    formRefresh: 60,
    notifs: undefined
  },
  created () {
    this.$http.get('/getTimeline').then(response => {
      this.notifs = response.body;
    })
  },
  methods: {
    followUsername: function(event){

        var data = {
            "screen_name": this.formFollow,
            "refresh_every": this.formRefresh
        };

        this.$http.post('/twitterFollowRegister', data, {
           emulateJSON: true
        }).then(function(){
            this.isActiveModal =false
        })
    }
  }
})


// lastCheck = moment().unix();

// function checkNotifs(){
//     $.ajax({
//         type: 'GET',
//         url: '/getTimeline',
//         // data to be added to query string:
//         data: { date: lastCheck },
//         dataType: 'json',
//         timeout: 300,
//         context: $('body'),
//         success: function(data){
//             // Supposing this JSON payload was received:
//             //   {"project": {"id": 42, "html": "<div>..." }}
//             // append the HTML to context object.
//             this.append(data.project.html)

//             lastCheck = moment().unix();
//         },
//         error: function(xhr, type){
//             alert('Ajax error!')
//         }
//     })
// }

// $(document).ready(function () {

//     //___________________Forms___________________

//     $('#twitterFollow').on('submit', function(e){
//         e.preventDefault();
//         var form = e.target;
//         var data = new FormData(form);

//         $.ajax({
//             type: 'POST',
//             url: "/twitterFollowRegister",
//             processData: false,
//             contentType: false,
//             data: data,
//             success: function(data){
//                 $('#result').text(data)
//             }
//         })
//     })

//     $('#linkAccount').on('submit', function(e){
//         e.preventDefault();
//         var form = e.target;
//         var data = new FormData(form);

//         $.ajax({
//             type: 'POST',
//             url: "/twitterRegister",
//             processData: false,
//             contentType: false,
//             data: data,
//             success: function(data){
//                 $('#result').text(data);
//             }
//         });
//     });

//     //________________Highlights_______________

//     var highlightMedia = function(element){

//         var parent = $(element.target).parents(".notifPanel")
//         $.each($('.twitterMedia[data-origin="'+ parent.attr("id") +'"]'), function(index,element){
//                 $(this).children("img").addClass("animated pulse infinite");
//         });
//     };

//     var unhighlightMedia = function(element){

//         $.each($('.twitterMedia'), function(index,element){
//                 $(this).children("img").removeClass("animated pulse infinite");
//         });
//     };

//     var highlightTweet = function(element){
//         var _id = $(element.target).parent().attr('data-origin')

//         $.each($('.notifPanel[id="'+ _id  +'"]'), function(index,element){
//             $(this).addClass("highlight animated tada");
//         });
//     };

//     var unhighlightTweet = function(element){
//         var _id = $(element.target).parent().attr('data-origin')

//         $.each($('.notifPanel[id="'+ _id  +'"]'), function(index,element){
//             $(this).removeClass("highlight animated tada");
//         });
//     };

//     $.each($('.notifPanel'),function(index,element){
//         $($(element).children()[1]).hover(highlightMedia,unhighlightMedia)
//     });

//     $.each($('.twitterMedia'),function(index,element){
//         $(element).on("mouseenter",highlightTweet);
//         $(element).on("mouseout",unhighlightTweet);
//     });

//     //update dates

//     function updateDates(){
//         $.each($('.humanDate'),function(index,element){
//             var date = $(this).attr('data-date');
//             var humanDate = moment(date);
//             $(this).text(humanDate.fromNow());
//         });
//     }

//     updateDates();
//     setTimeout(function(){location.reload()},180000);
// });

