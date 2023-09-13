import { relativeTimeThreshold } from "moment";
import React from "react"

export default class OpenApiWidget extends React.Component {

    constructor(...args) {
        super(...args)
        this.state = {
            loading: false,
            error: null,
            items: [],
            openAIResponse: "",
            qnaList: [],
            loadingAnswer: false,
        };
    }

    componentDidMount() {
        this.getOpenApiResponse(this.props.items, this.props.patient, this.props.type, this.props.role);
    }

    componentWillReceiveProps(newProps) {
        this.getOpenApiResponse(newProps.items, newProps.patient, newProps.type, newProps.role);
    }

    getOpenApiResponse(items, patient, type, role = 'patient') {
        this.setState({ loading: true, error: null }, () => {
            fetch("http://localhost:8000/openai",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ "patient": patient, "entries": items, "category": type, "role": role })
                }).then((response) => response.json())
                .then(data => {
                    this.state.openAIResponse = data.response;
                    this.setState({
                        ...this.state,
                        error: null,
                        loading: false
                    });
                })
                .catch(error => {
                    console.warn(error);
                    this.setState({
                        loading: false,
                        error
                    })
                })
        })
    }

    askQuestion = (evt) => {
        evt.preventDefault();
        let question = document.getElementById("question").value;
        this.setState({
            ...this.state,
            qnaList: [...this.state.qnaList, { "type": "question", "text": question }],
            loadingAnswer: true
        });
        document.getElementById("question").value = "";

        fetch("http://localhost:8000/openai",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ "patient": this.props.patient, "question": question })
            }).then((response) => response.json())
            .then(data => {
                this.setState({
                    ...this.state,
                    qnaList: [...this.state.qnaList, { "type": "answer", "text": data.response.choices[0].message.content }],
                    loadingAnswer: false
                });
            })
            .catch(error => {
                console.warn(error);
                this.setState({
                    ...this.state,
                    loadingAnswer: false,
                })
            })
    }

    render() {
        return (
            <div className="panel panel-default">
                <div className="panel-heading"><b className="text-primary"><i className="fa fa-magic" style={{ marginRight: 5 }}></i>Open AI - Summary</b></div>
                <div className="table-responsive" style={{ padding: 10 }}>
                    {
                        this.state.loading && <div style={{ textAlign: 'center' }}><i className="fa fa-spinner fa-spin fa-2x" title="Asking OpenAI..." style={{ margin: '20px auto' }}></i></div>
                    }
                    {
                        !this.state.loading && !this.state.error && this.state.openAIResponse && this.state.openAIResponse.choices &&
                        <div>
                            <span dangerouslySetInnerHTML={{ __html: this.state.openAIResponse.choices[0].message.content }}>
                            </span>
                            {this.state.qnaList.length > 0 && <hr style={{ clear: 'both', display: 'block', marginBottom: 10 }} />}
                            {
                                this.state.qnaList.map((qna, index) => {
                                    return (
                                        <div key={index}>
                                            <span dangerouslySetInnerHTML={{ __html: qna.text }}
                                                style={qna.type === 'answer' ?
                                                    { backgroundColor: '#337ab7', margin: '5px 20% 5px 5px', border: '1px #ccc solid', color: '#fff', borderRadius: 5, float: 'left', clear: 'both', padding: 10 } :
                                                    { textAlign: 'right', border: '1px #ccc solid', margin: '5px 5px 5px 20%', borderRadius: 5, float: 'right', clear: 'both', padding: 10 }}>
                                            </span>
                                        </div>
                                    )
                                })
                            }
                            {
                                this.state.loadingAnswer &&
                                <span style={{ backgroundColor: '#337ab7', margin: '5px 20px 5px 5px', border: '1px #ccc solid', color: '#fff', borderRadius: 5, float: 'left', clear: 'both', padding: 10 }}>
                                    <i className="fa fa-spinner fa-spin fa-2x" title="thinking..." style={{ margin: '10px' }}></i>
                                </span>
                            }
                            {this.state.qnaList.length > 0 && <hr style={{ clear: 'both', display: 'block', marginBottom: 10 }} />}
                            <form onSubmit={(event) => this.askQuestion(event)}>
                                <input type="text" id="question" className="form-control" placeholder="Ask your question..." disabled={this.state.loadingAnswer} />
                            </form>

                        </div>
                    }
                    {
                        this.state.error && "Error calling OpenAI - check the browser console"
                    }

                </div>
            </div>
        )
    }
}