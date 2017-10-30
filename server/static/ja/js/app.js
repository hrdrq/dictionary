INITIAL_DATA = 
{
  word: null,
  kana: null,
  accent: null,
  gogen: null,
  meaning: null,
  chinese: null,
  example: null,
  examples: null,
  listening_hint: null,
  audio: null,
  image: null,
  type: 'normal',
}
INITIAL_VARIABLE =
{
  meaning_list: [],
  audio_list: [],
  chinese_list: [],
  example_list: [],

  has_naver:false,
  no_forvo:false,

  multiple:false,
  meaning_selected: [],
  audio_selected: [],
  chinese_selected: [],
  example_selected: [],

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
  example_searching: false,

  saving:false,
  same_kana:null,

  test:false,
  // mobile用
  showing_side_bar:true,

  alternative_search_word:null,
  examples_group_id:0,
  update_showing_examples:false,
  has_yourei: null,
  yourei_index: 1,
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
    device: null
  },
  mounted () {
    this.device = $('#app').attr('device');
    this.meaning_editor = $('#meaning_edit');
    this.chinese_editor = $('#chinese_edit');
    if (this.device == 'mobile') {
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
        shortcutsEnabled:[],
        height: $(window).height()*0.5,
        charCounterCount: false,
        placeholderText: '日本語説明',
        toolbarButtonsMD:['html','fullscreen', 'bold', 'italic', 'underline', 'fontFamily', 'fontSize', 'insertLink', 'insertImage', 'insertTable', 'undo', 'redo'],
        toolbarButtonsSM: ['html','fullscreen', 'bold', 'italic', 'underline', 'fontFamily', 'fontSize', 'insertLink', 'insertImage', 'insertTable', 'undo', 'redo']
      });
      this.chinese_editor.froalaEditor({
        shortcutsEnabled:[],
        height: $(window).height()*0.5,
        charCounterCount: false,
        placeholderText: '中国語説明',
        htmlAllowedEmptyTags: ['span', 'textarea', 'a', 'iframe', 'object', 'video', 'style', 'script', '.fa'],
        toolbarButtonsMD:['html','fullscreen', 'bold', 'italic', 'underline', 'fontFamily', 'fontSize', 'insertLink', 'insertImage', 'insertTable', 'undo', 'redo'],
        toolbarButtonsSM: ['html','fullscreen', 'bold', 'italic', 'underline', 'fontFamily', 'fontSize', 'insertLink', 'insertImage', 'insertTable', 'undo', 'redo']
      });
    }
    $("a[href='https://froala.com/wysiwyg-editor']").parent().remove();
    $("#word").focus();

    // root = this;
    // $('#word').autocomplete({
    //     // open: function(event, ui) {
    //     //     $('.ui-autocomplete').off('menufocus hover mouseover mouseenter');
    //     // },
    //     source: function( req, res ) {

    //         $.ajax({
    //             url: "https://2omv62jpu3.execute-api.ap-northeast-1.amazonaws.com/prod/ja/suggest?word=" + encodeURIComponent(req.term),
    //             dataType: "json",
    //             success: function( response ) {
    //                 res(response.results);
    //             }
    //         });
    //     },
    //     // select: function (event, ui) {
    //     //   root.data.word = $('#word').val()
    //     //   // $("#txDestination").val(ui.item.label);
    //     //           // cityID = ui.item.id;
    //     //   return false;
    //     // },
    //     autoFocus: true,
    //     delay: 500,
    //     // minLength: 2
    // });
  },
  methods: {
    toggle_side_bar: function () {
      if(this.variable.showing_side_bar){
        $("#side_bar").css("right",-160)
        $("#toggle_side_bar").css("right",0)
        this.variable.showing_side_bar = false
      }else{
        $("#side_bar").css("right",0)
        $("#toggle_side_bar").css("right",160)
        this.variable.showing_side_bar = true
      }

    },
    search_query: function () {
      word = $('#word').val();
      var test = this.variable.test
      this.reset();
      word = word.replace(/ /g, '');
      $('#word').val(word)
      this.data.word = word
      root = this;
      if(test){
        root.search();
      }else{
        $.ajax({
            type: 'GET',
            url: API_HOST + 'search/query?word=' + this.data.word,
        })
        .done(function (res, ts, j) {
          if(res.status=='duplicated'){
            root.data.kana = res.result.kana;
            root.data.accent = res.result.accent;
            root.data.gogen = res.result.gogen;
            root.meaning_editor.froalaEditor('html.set', res.result.meaning);
            root.chinese_editor.froalaEditor('html.set', res.result.chinese);
            root.variable.duplicated = true;
            // root.variable.detail_id = res.result.detail_id;
            root.variable.duplicated_word = res.result
            $("#word").get(0).setSelectionRange(0,9999);
          }else{
            if(res.status == 'success'){
              root.variable.to_save = true;
            }else if(res.status == 'need_update'){
              root.variable.to_update = true;
              // root.variable.word_id = res.result.id;
              root.variable.duplicated_word = res.result
            }
            if ($(window).width() <= 499){
              document.activeElement.blur();
            }
            root.search();
          }
        });
      }
      
    },
    alternative_search: function(){
      asw = this.variable.alternative_search_word
      if(!asw || asw=='' /*|| asw==this.data.word*/)
        return;
      this.search(true)
    },
    search: function (alternative, update) {
      root = this
      this.variable.meaning_searching = true
      $.ajax({
          url: API_HOST + 'search/meaning?word=' + (alternative?this.variable.alternative_search_word: this.data.word),
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.meaning_searching = false;
        if(res.status=='success'){
          if(alternative){
            root.variable.meaning_list = root.variable.meaning_list.concat(res.results);
          }else{
            root.variable.meaning_list = res.results;
            root.variable.meaning_selected = []
            root.select_meaning(0);
          }
          
        }
      });
      if(!(this.variable.duplicated_word && this.variable.duplicated_word.type=='collect')){
        this.search_example(alternative)
      }
      

      if(!this.variable.to_update){
        this.variable.audio_searching = true
        $.ajax({
            url: API_HOST + 'search/audio/naver?word=' + (alternative?this.variable.alternative_search_word: this.data.word),
            type: 'GET',
        })
        .done(function (res, ts, j) {
          if(res.status=='success'){
            root.variable.audio_searching = false;
            if(alternative){
              root.variable.audio_list = root.variable.audio_list.concat(res.results);
            }else{
              
              root.variable.audio_list = res.results;
              root.variable.audio_selected = []
              root.select_audio(0);
              root.variable.has_naver = true;
            }
            
          }else{
            root.get_forvo(alternative);
          }
        });
      }

      this.variable.chinese_searching = true
      $.ajax({
          url: API_HOST + 'search/chinese?word=' + (alternative?this.variable.alternative_search_word: this.data.word),
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.chinese_searching = false;
        if(res.status=='success'){
          if(alternative){
            root.variable.chinese_list = root.variable.chinese_list.concat(res.results);
          }else{
            root.variable.chinese_list = res.results;
            root.variable.chinese_selected = []
            root.select_chinese(0);
          }
          
        }
      });
    },
    search_example: function(alternative, word, offset){
      this.variable.example_searching = true
      root = this
      if(!word){
        word = alternative?this.variable.alternative_search_word: this.data.word
      }
      $.ajax({
          url: API_HOST + 'search/example?word=' + word + (offset?("&offset="+((offset-1)*11+1)):''),
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.example_searching = false;
        if(res.status=='success'){
            if(res.type=='yourei'){
              root.variable.has_yourei = word
            }
            root.variable.examples_group_id += 1;
            res.results.forEach(function(r){
              r.examples_group_id = root.variable.examples_group_id
            });
          if(alternative){
            root.variable.example_list = root.variable.example_list.concat(res.results);
          }else{
            root.variable.example_list = res.results;
            root.variable.example_selected = []
            root.select_example(0);
          }
          
        }
      });
    },
    yourei_offset: function(){
      // swal({
      //   buttons: {
      //     cancel: true,
      //     confirm: "Confirm",
      //     roll: {
      //       text: "Do a barrell roll!",
      //       value: "roll",
      //     },
      //   },
      // });
      // return
      root = this
      
      swal({
        // title: "New offset",
        // content: "input",
        // inputType: "number",
        // showCancelButton: true,

        buttons: Array.from(Array(21).keys()).reduce(function(acc, cur, i) {
        if(i==0){
          acc["cancel"] = true
        }else{
          acc[i] = {text:i==root.variable.yourei_index?'['+i+']':i, value:i};
        }
        return acc;
      }, {})})

      .then((inputValue) => {
        // return
        if (inputValue === false) return false;
        
        // if (inputValue === "") {
        //   swal.showInputError("You need to write something!");
        //   return false
        // }
        root.variable.yourei_index = inputValue;
        root.variable.example_list = root.variable.example_list.filter(function(e){
          return e.examples_group_id !== root.variable.examples_group_id
        })
        root.search_example(null, root.variable.has_yourei, inputValue)

      });
    },
    get_forvo: function (alternative){
      this.variable.audio_searching = true
      root = this
      $.ajax({
          url: API_HOST + 'search/audio/forvo?word=' + (alternative?this.variable.alternative_search_word: this.data.word),
          type: 'GET',
      })
      .done(function (res, ts, j) {
        root.variable.audio_searching = false;
        if(res.status=='success'){
          if(alternative){
            root.variable.audio_list = root.variable.audio_list.concat(res.results);
          }else{
            root.variable.audio_list = root.variable.audio_list.concat(res.results);
            root.select_audio(0);
          }
          
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
    select_example: function (index){
      root = this;
      if(this.variable.multiple){
        example_selected = this.variable.example_selected;
        if(example_selected.includes(index)){
          example_selected.splice(example_selected.indexOf(index), 1);
        }else{
          example_selected.push(index);
        }
        example_str = ""
        listening_hint_str = ""
        
        example_selected.forEach(function(index){
          example = root.variable.example_list[index]
          example_str += (example.sentence + "<br>")
          listening_hint_str += (example.listening_hint + "<br>")
        });
        this.data.example = example_str.slice(0, -4);
        this.data.listening_hint = listening_hint_str.slice(0, -4);
      }else{
        if(this.variable.example_selected.indexOf(index) == -1){
          this.variable.example_selected = [index];
          example = this.variable.example_list[index]
          this.data.example = example.sentence;
          this.data.listening_hint = example.listening_hint;
        }else{
          this.variable.example_selected = [];
          this.data.example = this.data.listening_hint = this.data.examples = null;
        }
        
      }
      examples = ''
      examples_group_ids = []
      root.variable.example_selected.forEach(function(index){
        group_id = root.variable.example_list[index]['examples_group_id']
        if(examples_group_ids.indexOf(group_id) < 0){
          examples_group_ids.push(group_id)
        }
      });
      root.variable.example_list.forEach(function(example, index){
        if(root.variable.example_selected.indexOf(index) < 0 && examples_group_ids.indexOf(example['examples_group_id']) > -1){
          examples += '<p>' + example['sentence'] + '</p>'
        }
      });
      if(examples != ''){
        root.data.examples = examples
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
    save_query: function (){
      if(this.data.kana)
        this.data.kana = this.data.kana.replace(/ /g, '')
      if(!this.variable.multiple && (!this.data.kana || this.data.kana=='' || this.data.kana.match(/[一-龠]/))){
        // alert("カナを修正して");
        swal("カナを修正して")
        return;
      }
      this.variable.saving = true;
      root = this;
      if(this.variable.to_update){
        root.update();
      }else{
        if(this.data.kana && this.data.kana!=''){
          $.ajax({
              type: 'GET',
              url: API_HOST + 'save/query?kana=' + this.data.kana,
              contentType:'application/json',
          })
          .done(function (res, ts, j) {
            if(res.status=="duplicated"){
              root.variable.same_kana = res.results
              root.variable.saving = false;
            }else{
              root.save();
            }
          });
        }else{
          this.save()
        }
      }
    },
    save: function (){
      root = this
      original_data = this.data
      meaning = this.meaning_editor.froalaEditor('html.get', true)
      chinese = this.chinese_editor.froalaEditor('html.get', true)
      if(meaning != ''){
        original_data.meaning = meaning
      }
      if(chinese != ''){
        original_data.chinese = chinese
      }
      save_data = {}
      Object.keys(original_data).forEach(function (key) {
        if(original_data[key]!=null){
          save_data[key] = original_data[key];
        }
      });
      // if(root.variable.example_list.length>0){
      //   examples = ''
      //   root.variable.example_list.forEach(function(example, index){
      //     if(root.variable.example_selected.indexOf(index) < 0){
      //       examples += '<div class="ex">' + example['sentence'] + '</div>'
      //     }
      //   });
      //   if(examples != ''){
      //     save_data['examples'] = examples
      //   }
      // }
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
    update_edit: function (){
      dw = this.variable.duplicated_word
      to_push = {
        word: dw.word
      }
      keys= ['kana', 'accent', 'kanji', 'meaning', 'gogen']
      keys.forEach(function(key){
        if(key in dw){
          to_push[key] = dw[key]
        }
      })
      this.variable.meaning_list.push(to_push)
      this.select_meaning(0);
      if(dw.chinese){
        this.variable.chinese_list.push({
          word: dw.word,
          kanji: dw.word,
          meaning: dw.chinese
        })
        this.select_chinese(0);
      }
      this.variable.to_update = true
      // if(this.variable.duplicated_word.type!='collect'){
      //   this.search_example()
      // }
      
    },
    update: function (){
      root = this
      original_data = this.data
      meaning = this.meaning_editor.froalaEditor('html.get', true)
      chinese = this.chinese_editor.froalaEditor('html.get', true)
      if(meaning != ''){
        original_data.meaning = meaning
      }
      if(chinese != ''){
        original_data.chinese = chinese
      }
      update_data = {}
      Object.keys(original_data).forEach(function (key) {
        if(!(['word', 'type', 'image', 'audio'].includes(key)) && original_data[key]!=null){
          update_data[key] = original_data[key];
        }
      });
      update_data['id'] = this.variable.duplicated_word.id
      console.log(update_data);
      this.variable.saving = true;
      $.ajax({
          type: 'PUT',
          url: API_HOST + 'update',
          contentType:'application/json',
          data: JSON.stringify(update_data),
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
    add_alternative: function (){
      root = this
      this.variable.adding_alternative = true;
      $.ajax({
          url: API_HOST + 'save/add-alternative-word',
          type: 'POST',
          contentType:'application/json',
          data: JSON.stringify({word:this.variable.alternative, detail_id:this.variable.duplicated_word.detail_id}),
      })
      .done(function (res, ts, j) {
        root.variable.adding_alternative = false;
        if(res.status!="success"){
          alert(res.error_detail)
          root.variable.alternative = null;
        }
      });
    },
    merge: function (word, detail_id){
      root = this
      this.variable.saving = true;
      $.ajax({
          url: API_HOST + 'save/add-alternative-word',
          type: 'POST',
          contentType:'application/json',
          data: JSON.stringify({word:word, detail_id:detail_id}),
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
      this.meaning_editor.froalaEditor('html.set', '');
      this.chinese_editor.froalaEditor('html.set', '');
      this.data = Object.assign({}, INITIAL_DATA);
      Object.keys(INITIAL_VARIABLE).forEach(function(key){
         if(Object.prototype.toString.call( INITIAL_VARIABLE[key] ) === '[object Array]'){
          INITIAL_VARIABLE[key]=[]
        }
      });
      console.log(INITIAL_VARIABLE)
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
          app.save_query();
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
      case 'y':
          event.preventDefault();
          var a = document.createElement('a');
          a.href = '/proxy?url='+app.data.audio
          a.download = app.data.word+".mp3"
          a.style.display = 'none';
          document.body.appendChild(a);
          // $(a).click(function(evt){
          //     evt.preventDefault();
          //     var name = this.download;
          //     fetch("https://cors-anywhere.herokuapp.com/" + this.href)
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