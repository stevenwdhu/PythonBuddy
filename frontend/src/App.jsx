import React, { useState, useEffect, useRef } from 'react';
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/python/python';
import 'codemirror/addon/lint/lint.css';
import 'codemirror/addon/lint/lint';
import 'codemirror/addon/search/search';
import 'codemirror/addon/search/searchcursor';
import 'codemirror/addon/dialog/dialog';
import 'codemirror/addon/dialog/dialog.css';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import './App.css';

// Example codes
const examples = {
  1: "methods = []\nfor i in range(10):\n    methodds.append(lambda x: x + i)\nprint(methods[0](10))",
  2: "for i in range(5):\n    print(i)\n",
  3: "print([x*x for x in range(20) if x % 2 == 0])",
  4: "print(45**123)",
  5: "# Generator example\ndef genr(n):\n    i = 0\n    while i < n:\n        yield i\n        i += 1\n\nprint(list(genr(12)))\n",
  6: "# Class example\nclass Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def greet(self):\n        print(f'Hello, I am {self.name}')\n\np = Person('Alice', 30)\np.greet()\n",
  7: "# Fibonacci\ndef fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)\n\nfor i in range(10):\n    print(fib(i))\n"
};

const API_BASE = 'http://MyALB-743698351.us-east-1.elb.amazonaws.com';

function App() {
  const [code, setCode] = useState("def foo(bar, baz):\n    pass\nfoo(42)\n");
  const [output, setOutput] = useState('');
  const [errors, setErrors] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [sessionId] = useState(() => uuidv4());

  const editorRef = useRef(null);
  const textareaRef = useRef(null);
  const editorInstance = useRef(null);

  useEffect(() => {
    // Initialize CodeMirror
    if (textareaRef.current && !editorInstance.current) {
      editorInstance.current = CodeMirror.fromTextArea(textareaRef.current, {
        mode: 'python',
        lineNumbers: true,
        indentUnit: 4,
        matchBrackets: true,
        lint: true,
        styleActiveLine: true,
        gutters: ["CodeMirror-lint-markers"],
        extraKeys: {
          "Ctrl-Space": "autocomplete"
        }
      });

      editorInstance.current.on('change', (editor) => {
        const value = editor.getValue();
        setCode(value);
        checkCode(value);
      });

      // Set initial value
      editorInstance.current.setValue(code);
    }

    // Cleanup on unmount
    return () => {
      if (editorInstance.current) {
        const element = editorInstance.current.getWrapperElement();
        if (element && element.parentNode) {
          element.parentNode.removeChild(element);
        }
        editorInstance.current = null;
      }
    };
  }, []);

  const checkCode = async (codeToCheck) => {
    try {
      const response = await axios.post(`${API_BASE}/api/check_code`, {
        code: codeToCheck
      }, {
        headers: {
          'X-Session-ID': sessionId
        }
      });

      if (response.data && Array.isArray(response.data)) {
        setErrors(response.data);
      } else {
        setErrors([]);
      }
    } catch (error) {
      console.error('Error checking code:', error);
    }
  };

  const runCode = async () => {
    setIsRunning(true);
    setOutput('Running...');

    try {
      const response = await axios.post(`${API_BASE}/api/run_code`, {
        code: code
      }, {
        headers: {
          'X-Session-ID': sessionId
        }
      });

      if (response.data.error) {
        setOutput(response.data.error);
      } else {
        setOutput(response.data.output || 'No output');
      }
    } catch (error) {
      setOutput(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const loadExample = (exampleId) => {
    const exampleCode = examples[exampleId];
    if (exampleCode && editorInstance.current) {
      editorInstance.current.setValue(exampleCode);
      setCode(exampleCode);
      editorInstance.current.focus();
    }
  };

  useEffect(() => {
    // Cleanup session on unmount
    return () => {
      axios.post(`${API_BASE}/api/cleanup`, {}, {
        headers: {
          'X-Session-ID': sessionId
        }
      }).catch(err => console.error('Cleanup error:', err));
    };
  }, [sessionId]);

  return (
    <div className="App">
      <div className="header">
        <h1>Python Linter Online</h1>
        <p><i>Live Syntax Checking Using Pylint while Running Python</i></p>
        <div className="examples">
          <span>Examples: </span>
          {Object.keys(examples).map(id => (
            <React.Fragment key={id}>
              <a onClick={() => loadExample(id)}>{id}</a>
              {id !== '7' && ' '}
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="editor-container">
        <div ref={editorRef}>
          <textarea ref={textareaRef} defaultValue={code} />
        </div>
        <div className="controls">
          <button
            className="run-button"
            onClick={runCode}
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : 'Run'}
          </button>
        </div>
      </div>

      {output && (
        <div className="output-container">
          <h3>Output</h3>
          <pre className={`output ${output.startsWith('Error') ? 'error' : ''}`}>
            {output}
          </pre>
        </div>
      )}

      <div className="errors-container">
        <h2>Pylint Output Info</h2>
        {errors.length === 0 ? (
          <div className="no-errors">No errors or warnings found!</div>
        ) : (
          <table className="errors-table">
            <thead>
              <tr>
                <th>Line</th>
                <th>Severity</th>
                <th>Error</th>
                <th>Tips</th>
                <th>Error Code</th>
                <th>Error Info</th>
              </tr>
            </thead>
            <tbody>
              {errors.map((error, index) => {
                if (!error) return null;
                const severity = error.code && error.code[0] === 'E' ? 'error' : 'warning';
                return (
                  <tr key={index}>
                    <td>{error.line}</td>
                    <td>
                      <span className={`severity-${severity}`}>
                        {severity}
                      </span>
                    </td>
                    <td>{error.error}</td>
                    <td>{error.message}</td>
                    <td>{error.code}</td>
                    <td>{error.error_info}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <footer>
        Created by <a href="https://github.com/ethanchewy">Ethan Chiu</a>
      </footer>
    </div>
  );
}

export default App;

