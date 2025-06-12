const vscode = require('vscode');

let proseTerminal = null;

function activate(context) {
    let disposable = vscode.commands.registerCommand('prose.runFile', function () {
        const editor = vscode.window.activeTextEditor;

        if (editor) {
            editor.document.save();
            const filePath = editor.document.fileName;

            if (!proseTerminal || proseTerminal.exitStatus !== undefined) {
                proseTerminal = vscode.window.createTerminal("Prose Output");
            }
            proseTerminal.show();
            const command = `prose "${filePath}"`;
            proseTerminal.sendText(command);
        } else {
            vscode.window.showErrorMessage('Nenhum arquivo Prose aberto para executar.');
        }
    });

    context.subscriptions.push(disposable);
}

function deactivate() {
    if (proseTerminal) {
        proseTerminal.dispose();
    }
}

module.exports = {
    activate,
    deactivate
}
