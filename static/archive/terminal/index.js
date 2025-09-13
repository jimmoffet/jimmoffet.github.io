window.onload = function () {
  sessionStorage.clear();
  document.getElementById("user-input").focus();
};

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("user-input").focus();
});

window.onbeforeunload = function () {
  sessionStorage.clear();
  document.getElementById("user-input").focus();
};
var prompt = "guest@jamesdavidmoffet.com:/$";
var breadCrumbs = [prompt];
var commandHistory = [];
var defaultFolders = [
  "Applications",
  "Desktop",
  "Documents",
  "Music",
  "Pictures",
];
var currentDir = 0;
var items = [];
var id = 0;

function folder(name) {
  this.name = name;
}

function Item(id, name, type, parentId) {
  this.id = id;
  this.name = name;
  this.type = type;
  this.parent = parentId;
}

const ItemType = {
  TextFile: "txt",
  Dir: "dir",
};

items.push(new Item(id++, prompt, ItemType.Dir));

for (var i = 0; i < defaultFolders.length; i++) {
  items.push(new Item(id++, defaultFolders[i], ItemType.Dir, 0));
}

const terminal = {
  focus: function () {
    document.getElementById("user-input").focus();
  },
  echo: function (txt) {
    const history = document.getElementById("history");
    const div = document.createElement("div");
    const text = document.createTextNode(txt);
    div.append(txt);
    history.append(div);
    // console.log(txt);
  },
  startstream: function (txt, id) {
    const history = document.getElementById("history");
    const div = document.createElement("div");
    div.id = id;
    div.className = "terminal-output";
    txt = txt.replace(/\n/g, "<br>");
    div.innerHTML += txt;
    history.append(div);
  },
  stream: function (txt, id) {
    txt = txt.replace(/\n/g, "<br>");
    document.getElementById(id).innerHTML += txt;
  },
  input: function (e) {
    e.preventDefault();
    var input = document.getElementById("user-input");
    var txt = input.value;
    input.value = "";

    commandHistory.push(txt);
    this.echo(breadCrumbs.join("/") + " " + txt);

    var commandArr = txt.split(" ");

    if (Commands[commandArr[0]]) {
      Commands[commandArr[0]](commandArr);
    } else {
      // this.echo("Command not found: " + txt);
      Commands["chat"](commandArr);
    }
  },
};

const Commands = {
  // rmdir: (arr) => {
  //   items = items.filter((item) => {
  //     return item.name != arr[1];
  //   });
  // },
  // nano: (arr) => {
  //   const editor = new nanoEditor("nano-editor", "javascript", true);
  //   editor.onChange((val) => {
  //     console.log(val);
  //   });
  //   document
  //     .querySelector("#nano-editor textarea")
  //     .addEventListener("keydown", function (event) {
  //       if (event.ctrlKey && event.key === "x") {
  //         console.log("Control + X pressed!");
  //         // Do something else here
  //       }
  //     });
  // },
  // mkdir: (arr) => {
  //   items.push(new Item(id++, arr[1], ItemType.Dir, currentDir));
  // },
  // touch: (arr) => {
  //   items.push(new Item(id++, arr[1], ItemType.Text, currentDir));
  // },
  clear: (arr) => {
    commandHistory = [];
    document.getElementById("history").innerHTML = "";
  },
  // cd: (arr) => {
  //   var found = false;
  //   for (var i = 0; i < items.length; i++) {
  //     if (items[i].name == arr[1] && items[i].type == ItemType.Dir) {
  //       found = true;
  //       breadCrumbs.push(items[i].name);
  //       currentDir = items[i].id;
  //       document.querySelector(".bread-crumbs").innerText =
  //         breadCrumbs.join("/") + " $ ";
  //     } else if (arr[1] == "../") {
  //       breadCrumbs.pop();
  //       document.querySelector(".bread-crumbs").innerText =
  //         breadCrumbs.join("/") + " $ ";
  //     }
  //   }
  //   if (!found) {
  //     terminal.echo("cd: Directory not found");
  //   }
  // },
  // ls: (arr) => {
  //   var list = "";
  //   var filteredArr = items
  //     .filter((item) => {
  //       return item.parent == currentDir;
  //     })
  //     .map((item) => {
  //       return item.name;
  //     });
  //   terminal.echo(filteredArr.join(" "));
  // },
  // cat: (arr) => {
  //   console.log("cat");
  // },
  chat: (arr) => {
    message = arr.join(" ");
    startChat(message);
  },
};

async function startChat(message) {
  let messages = sessionStorage.getItem("bot-message");
  if (messages == null) {
    messages = [
      {
        role: "system",
        content:
          "You are a helpful, but terminal emulator who only knows about Jim Moffet's professional life and work. All of your responses should look like the result of a terminal command, where the information about jim moffet that you are providing has come from data available to your terminal. If the user needs help or types 'help', show a list of commands that someone might use when exploring a computer full of data about jim moffet. You can make up directories and filenames, but they should be plausible.",
      },
      {
        role: "user",
        content: "What is this?",
      },
      {
        role: "assistant",
        content:
          "command not found: What is this? -- \n \n Try typing 'help' to see a list of commands.",
      },
      {
        role: "user",
        content: "cat jim_moffet_bio.txt",
      },
      {
        role: "assistant",
        content:
          "Jim is a generalist, technologist, and entrepreneur. He was the founding product head at Y Combinator-backed Impactive, the folks behind the ‘Vote Joe’ mobile organizing platform for President Biden's campaign in 2020. He was a researched Civic Tech as a Fulbright Fellow in Budapest. Jim guest lectured on Civic Tech and Federated Learning at Carnegie Mellon University. He is currently a Technologist at 10x, the Federal Government’s Venture Studio for public interest technology.",
      },
      {
        role: "user",
        content: "cat jim_moffet_bio.txt | grep current job",
      },
      {
        role: "assistant",
        content:
          "Jim Moffet currently works at currently a Technologist at 10x, the Federal Government’s Venture Studio for public interest technology.",
      },
      {
        role: "user",
        content: "Tell me about jim moffet's current job",
      },
      {
        role: "assistant",
        content:
          "Result of $find jim moffet current job: \n \n jim_moffet_bio.txt: Jim Moffet currently works at currently a Technologist at 10x, the Federal Government’s Venture Studio for public interest technology.",
      },
    ];
  } else {
    messages = JSON.parse(messages);
  }
  // console.log(messages);
  messages.push({ role: "user", content: message });

  var es = await fetch("https://api.openai.com/v1/chat/completions", {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    method: "POST",
    body: JSON.stringify({
      model: "gpt-3.5-turbo",
      messages: messages,
      stream: true,
      stop: ["\n\n"],
    }),
  });

  const reader = es.body?.pipeThrough(new TextDecoderStream()).getReader();

  var message_text = "";
  let message_id = messages.length.toString();

  while (true) {
    const res = await reader?.read();
    if (res?.done) {
      // console.log(`message_text is ${message_text}`);
      messages.push({ role: "assistant", content: message_text });
      sessionStorage.setItem("bot-message", JSON.stringify(messages));
      break;
    }
    const jsonStrings = res?.value.match(/data: (.*)\n\n/g);

    const jsonData = jsonStrings.map((jsonString) => {
      const startIndex = jsonString.indexOf("{");
      const endIndex = jsonString.lastIndexOf("}") + 1;
      const json = jsonString.substring(startIndex, endIndex);
      let data;

      try {
        if (json) {
          data = JSON.parse(json);
          if (data.choices[0].delta.finish_reason != "stop") {
            let text = data.choices[0].delta.content;
            if (text) {
              let i = 0;
              while (i < text.length) {
                // document.getElementById("demo").innerHTML += text.charAt(i);

                if (message_text === "") {
                  terminal.startstream(text.charAt(i), message_id);
                } else {
                  terminal.stream(text.charAt(i), message_id);
                }
                message_text += text.charAt(i);
                i++;
              }
            }
          }
        }
      } catch (ex) {
        console.log(`error: ${ex}`);
        // console.log(json);
      }
      return data;
    });
  }
}
