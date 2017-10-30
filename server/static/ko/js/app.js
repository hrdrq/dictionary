INITIAL_DATA = 
{
  word: null,
  origin: null,
  pronounce: null,
  meaning: null,
  chinese: null,
  japanese: null,
  audio: null,
  image: null,
}
INITIAL_VARIABLE =
{
  meaning_list: [],
  audio_list: [],
  chinese_list: [],
  japanese_list: [],

  meaning_trans: null,

  has_naver:false,
  no_forvo:false,

  multiple:false,
  meaning_selected: [],
  audio_selected: [],
  chinese_selected: [],
  japanese_selected: [],

  to_save: false,
  duplicated: false,

  meaning_searching: false,
  audio_searching: false,
  chinese_searching: false,
  japanese_searching: false,

  saving:false,
}
var app = new Vue({
  el: '#app',
  data: {
    data: Object.assign({}, INITIAL_DATA),
    variable: Object.assign({}, INITIAL_VARIABLE),
    // meaning_editor: null,
    chinese_editor: null,
    // japanese_editor: null,
  },
  mounted () {
    this.chinese_editor = $('#chinese_edit');
    if ($(window).width() <= 499) {
      this.chinese_editor.froalaEditor({
        height: window.innerHeight*0.5,
        charCounterCount: false,
        toolbarInline: true,
        placeholderText: '中国語説明',
        htmlAllowedEmptyTags: ['span', 'textarea', 'a', 'iframe', 'object', 'video', 'style', 'script', '.fa']
      });
      $("#search_tool").css({"height": (window.innerHeight-$("#forPhone").height())});
    }else{
      this.chinese_editor.froalaEditor({
        height: $(window).height()*0.5,
        charCounterCount: false,
        placeholderText: '中国語説明',
        htmlAllowedEmptyTags: ['span', 'textarea', 'a', 'iframe', 'object', 'video', 'style', 'script', '.fa']
      });
      console.log($(window).height()*0.5)
      $('#left textarea, #left div').css('height',$('div#right').height()*0.3)
    }
    $("a[href='https://froala.com/wysiwyg-editor']").parent().remove();
    $("#word").focus();

  },
  methods: {
    search_query: function () {
      word = $('#word').val();
      this.reset();
      this.data.word = word;
      root = this;
      $.ajax({
          type: 'GET',
          url: API_HOST + 'search/query?word=' + this.data.word,
      })
      .done(function (res, ts, j) {
        if(res.status=='duplicated'){
          root.data.pronounce = res.result.pronounce;
          root.data.origin = res.result.origin;
          root.data.meaning = res.result.meaning;
          root.data.japanese = res.result.japanese;
          root.chinese_editor.froalaEditor('html.set', res.result.chinese);
          root.variable.duplicated = true;
          // root.variable.detail_id = res.result.detail_id;
          root.variable.duplicated_word = res.result
          $("#word").get(0).setSelectionRange(0,9999);
        }else{
          if(res.status == 'success'){
            root.variable.to_save = true;
          }
          if ($(window).width() <= 499){
            document.activeElement.blur();
          }
          root.search();
        }
      });
    },
    search: function () {
      root = this
      this.variable.meaning_searching = true
      this.variable.audio_searching = true
      $.ajax({
          url: API_HOST + 'search/meaning?word=' + this.data.word,
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.meaning_searching = false;
        root.variable.audio_searching = false
        if(res.status=='success'){
          root.variable.audio_list = []
          res.results.forEach(function(r){
            if(r['audio']){
              var audio = {url: r['audio']} 
              delete r['audio']
              audio.word = r.origin?(r.word+'('+r.origin+')'):r.word
              root.variable.audio_list.push(audio)
            }
          })
          root.variable.meaning_list = res.results;
          root.variable.meaning_selected = []
          root.select_meaning(0);
          
          if(root.variable.audio_list.length>0){
            root.variable.has_naver = true;
            root.variable.audio_selected = []
            root.select_audio(0);
          }else{
            root.get_forvo();
          }
          
        }else{
          root.get_forvo();
        }
      });

      // if(!this.variable.to_update){
      //   this.variable.audio_searching = true
      //   $.ajax({
      //       url: API_HOST + 'search/audio/naver?word=' + this.data.word,
      //       type: 'GET',
      //   })
      //   .done(function (res, ts, j) {
      //     if(res.status=='success'){
      //       root.variable.audio_searching = false;
      //       root.variable.audio_list = res.results;
      //       root.variable.audio_selected = []
      //       root.select_audio(0);
      //       root.variable.has_naver = true;
      //     }else{
      //       root.get_forvo();
      //     }
      //   });
      // }

      this.variable.japanese_searching = true
      $.ajax({
          url: API_HOST + 'search/japanese?word=' + this.data.word,
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.japanese_searching = false;
        if(res.status=='success'){
          root.variable.japanese_list = res.results;
          root.variable.japanese_selected = []
          root.select_japanese(0);
        }
      });

      this.variable.chinese_searching = true
      $.ajax({
          url: API_HOST + 'search/chinese?word=' + this.data.word,
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.chinese_searching = false;
        if(res.status=='success'){
          root.variable.chinese_list = res.results;
          root.variable.chinese_selected = []
          root.select_chinese(0);
        }
      });
    },
    get_forvo: function (){
      this.variable.audio_searching = true
      root = this
      $.ajax({
          url: API_HOST + 'search/audio/forvo?word=' + this.data.word,
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.audio_searching = false;
        if(res.status=='success'){
          root.variable.audio_list = root.variable.audio_list.concat(res.results);
          root.select_audio(0);
        }
        else{
          root.variable.no_forvo = true;
        }
      });
    },
    add_forvo: function (){
      // add_word = prompt("Forvoに追加？",this.data.word);
      // if(add_word && add_word != ""){
      //   this.variable.audio_searching = true
      //   root = this
      //   $.ajax({
      //       url: API_HOST + 'search/audio/forvo/add?word=' + add_word,
      //       type: 'GET',
      //   })
      //   .done(function (res, ts, j) {
      //     root.variable.audio_searching = false;
      //     if(res.status=='success'){
  
      //     }
      //   });
      // }
      var self = this
      swal({
        title: "Forvoに追加？",
        // text: "Write something interesting:",
        type: "input",
        inputValue:this.data.word,
        showCancelButton: true,
        // closeOnConfirm: false,
        // animation: "slide-from-top",
        // inputPlaceholder: "Write something"
      },
      function(inputValue){
        if (inputValue === false) return false;
        
        if (inputValue === "") {
          swal.showInputError("You need to write something!");
          return false
        }
        self.variable.no_forvo=false
        
        self.variable.audio_searching = true
        $.ajax({
            url: API_HOST + 'search/audio/forvo/add?word=' + inputValue,
            type: 'GET',
        })
        .done(function (res, ts, j) {
          self.variable.audio_searching = false;
          if(res.status=='success'){
  
          }
        });
      });
    },
    select_meaning: function (index){
      if(this.variable.multiple){
        meaning_selected = this.variable.meaning_selected;
        if(meaning_selected.includes(index)){
          // meaning_selected.pop(index);
          meaning_selected.splice(meaning_selected.indexOf(index), 1);
        }else{
          meaning_selected.push(index);
        }
        meaning_html = "";
        root = this;
        meaning_selected.forEach(function(index){
          meaning = root.variable.meaning_list[index]
          // meaning_html += '<div style="font-size: 120%;font-weight: bold">'+(meaning.pronounce?meaning.pronounce:'')+" "+(meaning.origin?meaning.origin:'')+'</div>';
          meaning_html += (meaning_html==''?'':'\n')+meaning.meaning;
        });
        this.data.meaning = meaning_html
        // this.meaning_editor.froalaEditor('html.set', meaning_html);
        this.data.pronounce = this.data.origin = null;
      }else{
        if(this.variable.meaning_selected.indexOf(index) == -1){
          this.variable.meaning_selected = [index];
          meaning = this.variable.meaning_list[index]
          this.data.pronounce = meaning.pronounce;
          this.data.origin = meaning.origin;
          // this.meaning_editor.froalaEditor('html.set', meaning.meaning);
          this.data.meaning = meaning.meaning
          this.variable.meaning_trans = meaning.translate
        }else{
          this.variable.meaning_selected = [];
          this.data.pronounce = this.data.origin = null;
          // this.meaning_editor.froalaEditor('html.set', '');
          this.data.meaning = ''
          this.variable.meaning_trans = null
        }
        
      }
    },
    select_audio: function (index){
      if(this.variable.multiple){
        audio_selected = this.variable.audio_selected;
        if(audio_selected.includes(index)){
          audio_selected.splice(audio_selected.indexOf(index), 1);
        }else{
          audio_selected.push(index);
        }
        audio_dict_list = []
        root = this;
        audio_selected.forEach(function(index){
          audio = root.variable.audio_list[index]
          audio_dict_list.push({file_name: audio.word, url: audio.url})
        });
        this.data.audio = audio_dict_list;
      }else{
        if(this.variable.audio_selected.indexOf(index) == -1){
          this.variable.audio_selected = [index];
          this.data.audio = this.variable.audio_list[index].url
        }else{
          this.variable.audio_selected = [];
          this.data.audio = null;
        }
      }
    },
    play_audio: function (index){
      url = this.variable.audio_list[index].url
      var audio = new Audio(url);
      audio.play();
    },
    select_japanese: function (index){
      if(this.variable.multiple){
        japanese_selected = this.variable.japanese_selected;
        if(japanese_selected.includes(index)){
          // meaning_selected.pop(index);
          japanese_selected.splice(japanese_selected.indexOf(index), 1);
        }else{
          japanese_selected.push(index);
        }
        japanese_html = "";
        root = this;
        japanese_selected.forEach(function(index){
          japanese = root.variable.japanese_list[index]
          // japanese_html += '<div style="font-size: 120%;font-weight: bold">'+(japanese.kana?japanese.kana:'')+" "+(japanese.accent?japanese.accent:'')+" "+(japanese.gogen?japanese.gogen:'')+'</div>';
          // japanese_html += '<div>'+japanese.meaning+'</div>';
          japanese_html += (japanese_html==''?'':'\n')+japanese.meaning;
        });
        this.data.japanese = japanese_html
        // this.meaning_editor.froalaEditor('html.set', meaning_html);
      }else{
        if(this.variable.japanese_selected.indexOf(index) == -1){
          this.variable.japanese_selected = [index];
          meaning = this.variable.japanese_list[index]
          this.data.japanese = meaning.meaning
        }else{
          this.variable.japanese_selected = [];
          this.data.pronounce = this.data.origin = null;
          // this.meaning_editor.froalaEditor('html.set', '');
          this.data.japanese = ''
        }
        
      }
    },
    select_chinese: function (index){
      if(this.variable.multiple){
        chinese_selected = this.variable.chinese_selected;
        if(chinese_selected.includes(index)){
          chinese_selected.splice(chinese_selected.indexOf(index), 1);
        }else{
          chinese_selected.push(index);
        }
        chinese_html = "";
        root = this;
        chinese_selected.forEach(function(index){
          chinese = root.variable.chinese_list[index]
          // chinese_html += '<div style="font-size: 120%;font-weight: bold">'+chinese.kana+'</div>';
          chinese_html += '<div>'+chinese.meaning+'</div>';
        });
        this.data.chinese = chinese_html
        // this.chinese_editor.froalaEditor('html.set', chinese_html);
      }else{
        if(this.variable.chinese_selected.indexOf(index) == -1){
          this.variable.chinese_selected = [index];
          this.data.chinese = this.variable.chinese_list[index].meaning
          this.chinese_editor.froalaEditor('html.set', this.data.chinese);
        }else{
          this.variable.chinese_selected = [];
          this.data.chinese = null;
          this.chinese_editor.froalaEditor('html.set', '');
        }
      }
    },
    image_change: function (e){
      file = e.target.files[0]
      root = this
      canvas = document.getElementById('image_show');
      ctx = canvas.getContext("2d");
      var reader = new FileReader();
      reader.onload = function(event){
          var img = new Image();
          
          img.onload = function(){
            var MAX_WIDTH = 350;
            if(img.width>MAX_WIDTH){
              canvas.width = MAX_WIDTH;
              canvas.height = (MAX_WIDTH*img.height)/img.width;
            }else{
                canvas.width = img.width;
                canvas.height = img.height;
            } 
            ctx.drawImage(img,0,0,canvas.width,canvas.height);
            root.data.image = canvas.toDataURL("image/png").replace(/^data:image\/(png|jpg);base64,/, "");
          }
          img.src = event.target.result;
      }
      reader.readAsDataURL(e.target.files[0]);
    },
    save: function (){
      root = this
      original_data = this.data
      // meaning = this.meaning_editor.froalaEditor('html.get', true)
      chinese = this.chinese_editor.froalaEditor('html.get', true)
      // if(meaning != ''){
      //   original_data.meaning = meaning
      // }
      if(chinese != ''){
        original_data.chinese = chinese
      }
      save_data = {}
      Object.keys(original_data).forEach(function (key) {
        if(original_data[key]!=null){
          save_data[key] = original_data[key];
        }
      });
      console.log(save_data);
      this.variable.saving = true;
      $.ajax({
          type: 'POST',
          url: API_HOST + 'save',
          contentType:'application/json',
          data: JSON.stringify(save_data),
      })
      .done(function (res, ts, j) {
        root.variable.saving = false;
        if(res.status!="success"){
          alert(res.error_detail)
        }else{
          root.reset();
        }
      });
    },
    reset: function (){
      // this.meaning_editor.froalaEditor('html.set', '');
      this.chinese_editor.froalaEditor('html.set', '');
      this.data = Object.assign({}, INITIAL_DATA);
      this.variable = Object.assign({}, INITIAL_VARIABLE);
      // console.log(this.variable,INITIAL_VARIABLE)
      canvas = document.getElementById('image_show');
      context = canvas.getContext('2d');
      context.clearRect(0, 0, canvas.width, canvas.height);
      $("#word").focus();
    },
  }
})

$(window).bind('keydown', function(event) {
  if (event.ctrlKey || event.metaKey) {
    switch (String.fromCharCode(event.which).toLowerCase()) {
      case 's':
          event.preventDefault();
          app.save();
          // alert('ctrl-s');
          break;
      case 'd':
          event.preventDefault();
          
          $( "#image_loader" ).click();
          // alert('ctrl-f');
          break;
      case 'g':
          event.preventDefault();
          $("#word").select();
          // alert('ctrl-g');
          break;
      case 'b':
          event.preventDefault();
          app.play_audio(0);
          // $("#word").select();
          // alert('ctrl-b');
          break;
      case 'h':
          event.preventDefault();
          app.play_audio(1);
          // $("#word").select();
          // alert('ctrl-h');
          break;
      case 'u':
          event.preventDefault();
          app.play_audio(2)
          // $("#word").select();
          // alert('ctrl-u');
          break;
      case 'j':
          event.preventDefault();
          app.add_forvo()
          break;
    }
  }
});
function click_focus(){
  $("#word").focus();
  $("#word").get(0).setSelectionRange(0,9999);
  $(window).scrollTop($('#word').offset().top)
  // $('html, body').animate({
  //     scrollTop: ($('#word').offset().top)
  // },1);
}