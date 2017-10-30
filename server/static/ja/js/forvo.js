INITIAL_DATA = 
{
  word: null,
  kana: null,
  accent: null,
  gogen: null,
  meaning: null,
  chinese: null,
  audio: null,
  image: null,
  type: 'normal',
  addReverse: null,
}
INITIAL_VARIABLE =
{
  meaning_list: [],
  audio_list: [],
  chinese_list: [],

  has_naver:false,
  no_forvo:false,

  multiple:false,
  meaning_selected: [],
  audio_selected: [],
  chinese_selected: [],

  to_save: false,
  to_update: false,
  duplicated: false,

  alternative: null,
  duplicated_word: null,
  // word_id: null,
  // detail_id: null,
  adding_alternative: false,

  meaning_searching: false,
  audio_searching: false,
  chinese_searching: false,

  saving:false,
  same_kana:null,
}
var app = new Vue({
  el: '#app',
  data: {
    data: Object.assign({}, INITIAL_DATA),
    variable: Object.assign({}, INITIAL_VARIABLE),
    type_options: [
      { text: '普通', value: 'normal' },
      { text: 'IT', value: 'IT' },
      { text: '名前', value: 'name' },
    ],
    meaning_editor: null,
    chinese_editor: null,
    text_of_textarea: null,
  },
  mounted () {
    this.meaning_editor = $('#meaning_edit');
    this.chinese_editor = $('#chinese_edit');
    if ($(window).width() <= 499) {
      this.meaning_editor.froalaEditor({
        height: window.innerHeight*0.5,
        charCounterCount: false,
        toolbarInline: true,
        placeholderText: '日本語説明'
      });
      this.chinese_editor.froalaEditor({
        height: window.innerHeight*0.5,
        charCounterCount: false,
        toolbarInline: true,
        placeholderText: '中国語説明',
        htmlAllowedEmptyTags: ['span', 'textarea', 'a', 'iframe', 'object', 'video', 'style', 'script', '.fa']
      });
      $("#search_tool").css({"height": (window.innerHeight-$("#forPhone").height())});
    }else{
      this.meaning_editor.froalaEditor({
        height: $(window).height()*0.5,
        charCounterCount: false,
        placeholderText: '日本語説明'
      });
      this.chinese_editor.froalaEditor({
        height: $(window).height()*0.5,
        charCounterCount: false,
        placeholderText: '中国語説明',
        htmlAllowedEmptyTags: ['span', 'textarea', 'a', 'iframe', 'object', 'video', 'style', 'script', '.fa']
      });
    }
    $("a[href='https://froala.com/wysiwyg-editor']").parent().remove();
    $("#word").focus();

    // root = this;
  },
  methods: {
    loadTextArea: function (){
      words = this.text_of_textarea.split('.mp3\n');
      word = words.shift()
      this.data.word = word
      this.text_of_textarea = words.join('.mp3\n');
      this.search(word);

      // lines = $("#toAddAudio").val().split('.mp3\n');
      // $("#word").val(lines[0]);
      // $("#search").submit();
      // x++;
    },
    search: function (word) {
      console.log(word)
      // word = $('#word').val();
      this.reset();
      this.data.word = word;
      root = this;
      $.ajax({
          type: 'GET',
          url: API_HOST + 'search/query?word=' + this.data.word,
      })
      .done(function (res, ts, j) {
        root.data.kana = res.result.kana;
        root.data.accent = res.result.accent;
        root.data.gogen = res.result.gogen;
        root.meaning_editor.froalaEditor('html.set', res.result.meaning);
        root.chinese_editor.froalaEditor('html.set', res.result.chinese);
        root.variable.duplicated = true;
        // root.variable.detail_id = res.result.detail_id;
        root.variable.duplicated_word = res.result
        root.get_forvo();
      });
    },
    search2: function () {
      root = this
      this.variable.meaning_searching = true
      $.ajax({
          url: API_HOST + 'search/meaning?word=' + this.data.word,
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.meaning_searching = false;
        if(res.status=='success'){
          root.variable.meaning_list = res.results;
          root.variable.meaning_selected = []
          root.select_meaning(0);
        }
      });

      root.get_forvo();

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
      var self = this
      swal({
        title: "Forvoに追加？",
        // text: "Write something interesting:",
        content: {
          element: "input",
          attributes: {
            value: self.data.word,

          },
        },
        buttons: {
          cancel: 'キャンセル',
          confirm: {
            text: "OK",
            value: true,
            visible: true,
            className: "",
            closeModal: true
          }
        },
      })
      .then((inputValue) => {
        console.log('inputValue',inputValue)
        if (!inputValue) inputValue = self.data.word;
        
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
          meaning_html += '<div style="font-size: 120%;font-weight: bold">'+(meaning.kana?meaning.kana:'')+" "+(meaning.accent?meaning.accent:'')+" "+(meaning.gogen?meaning.gogen:'')+'</div>';
          meaning_html += '<div>'+meaning.meaning+'</div>';
        });
        this.meaning_editor.froalaEditor('html.set', meaning_html);
        this.data.kana = this.data.accent = this.data.gogen = null;
      }else{
        if(this.variable.meaning_selected.indexOf(index) == -1){
          this.variable.meaning_selected = [index];
          meaning = this.variable.meaning_list[index]
          this.data.kana = meaning.kana;
          this.data.accent = meaning.accent;
          this.data.gogen = meaning.gogen;
          this.meaning_editor.froalaEditor('html.set', meaning.meaning);
        }else{
          this.variable.meaning_selected = [];
          this.data.kana = this.data.accent = this.data.gogen = null;
          this.meaning_editor.froalaEditor('html.set', '');
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
          chinese_html += '<div style="font-size: 120%;font-weight: bold">'+chinese.kana+'</div>';
          chinese_html += '<div>'+chinese.meaning+'</div>';
        });
        this.chinese_editor.froalaEditor('html.set', chinese_html);
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
    save: function (){

      var a = document.createElement('a');
      a.href = '/proxy?url='+app.data.audio
      a.download = this.data.word+".mp3"
      a.style.display = 'none';
      document.body.appendChild(a);
      // console.log(a)
      // $(a).click(function(evt){
      //     evt.preventDefault();
      //     var name = this.download;
         
      //     // we need a blob so we can create a objectURL and use it on a link element
      //     // jQuery don't support responseType = 'blob' (yet)
      //     // So I use the next version of ajax only avalible in blink & firefox
      //     // it also works fine by using XMLHttpRequest v2 and set the responseType
      //     fetch("https://cors-anywhere.herokuapp.com/" + this.href)
      //         // res is the beginning of a request it only gets the response headers
      //         // here you can use .blob() .text() .json or res.arrayBuffer() depending
      //         // on what you need, if it contains Content-Type: application/json
      //         // then you might want to choose res.json() 
      //         // all this returns a promise
      //         .then(res => res.blob())
      //         .then(blob => {
      //             $("<a>").attr({
      //                 download: name,
      //                 href: URL.createObjectURL(blob)
      //             })[0].click();
      //         });
      // });
      a.click()
      delete a;
      // alert('x')

      this.reset();
      this.loadTextArea()
    },
    reset: function (){
      this.meaning_editor.froalaEditor('html.set', '');
      this.chinese_editor.froalaEditor('html.set', '');
      this.data = Object.assign({}, INITIAL_DATA);
      this.variable = Object.assign({}, INITIAL_VARIABLE);
      canvas = document.getElementById('image_show');
      context = canvas.getContext('2d');
      context.clearRect(0, 0, canvas.width, canvas.height);
      $("#word").focus();
    },
    focus_add_alternative: function (){
      $("#add_alternative").focus();
    },
  }
})

function key_handler(){

}
// $('#meaning_edit').froalaEditor({
//   height: $(window).height()*0.5,
//   charCounterCount: false,
//   placeholderText: 'Japanese meaning'
// });
// $('#chinese_edit').froalaEditor({
//   height: $(window).height()*0.5,
//   charCounterCount: false,
//   placeholderText: 'Chinese meaning'
// });
$(window).bind('keydown', function(event) {
  if (event.ctrlKey || event.metaKey) {
    switch (String.fromCharCode(event.which).toLowerCase()) {
      case 's':
          event.preventDefault();
          app.save();
          // alert('ctrl-s');
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