import React from "react"
import './AnomalyAlert.less';
export default class AnomalyAlert extends React.Component {

    constructor(...args) {
        super(...args)
        this.state = {
            loading: true,
            error: null,
            items: [],
            openAIResponse: "",
            hover: false,
            alertsFound: false
        };
    }

    handleMouseIn() {
      this.setState({ hover: true })
    }

    handleMouseOut() {
      this.setState({ hover: false })
    }

    componentDidMount() {
        this.getOpenApiResponse(this.props.items, this.props.patient, this.props.type, this.props.role);
    }

    getOpenApiResponse(items, patient, type, role = 'patient') {
        this.setState({ loading: true, error: null }, () => {
            fetch("http://localhost:8000/openaialerts",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ "patient": patient, "entries": items, "category": type, "role": role })
                }).then((response) => response.json())
                .then(data => {
                    this.setState({
                        ...this.state,
                        openAIResponse: data.response,
                        error: null,
                        loading: false
                    });
                    console.log(data.any_alerts_check.choices[0].message.content.toUpperCase().includes("NO"));
                    if (data.any_alerts_check.choices[0].message.content.toUpperCase().includes("NO")) {
                        this.setState({ alertsFound: false });
                    } else {
                        this.setState({ alertsFound: true });
                    }
                    console.log(this.state.alertsFound);
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


    render() {
        const displayOnHover = {
          display: this.state.hover ? 'block' : 'none'
        }
        console.log(this.state.error);
        return (
          <div className="patient-anomaly-alert">
            {this.state.loading && <i className="fa fa-solid fa-spinner fa-spin" aria-hidden="true"></i> }
            {!this.state.loading && this.state.alertsFound && !this.state.error &&
              <div>
                <div onMouseOver={this.handleMouseIn.bind(this)} onMouseOut={this.handleMouseOut.bind(this)}>
                  <i className="fa fa-exclamation-circle alerts-found" aria-hidden="true"></i>
                </div>
                <div className="tooltipWrapper">
                  <div className="tooltipStyle" style={displayOnHover}>
                    <span dangerouslySetInnerHTML={{__html: this.state.openAIResponse.choices[0].message.content}}></span>
                  </div>
                </div>
              </div>
            }
            {!this.state.loading && !this.state.alertsFound && !this.state.error &&
              <div>
                <div onMouseOver={this.handleMouseIn.bind(this)} onMouseOut={this.handleMouseOut.bind(this)}>
                  <i className="fa fa-exclamation-circle" aria-hidden="true"></i>
                </div>
                <div className="tooltipWrapper">
                  <div className="tooltipStyle" style={displayOnHover}>
                    <span>No alerts found.</span>
                  </div>
                </div>
              </div>
            }
            {!this.state.loading && this.state.error &&
              <div>
                <div onMouseOver={this.handleMouseIn.bind(this)} onMouseOut={this.handleMouseOut.bind(this)}>
                  <i className="fa fa-exclamation-circle alerts-error" aria-hidden="true"></i>
                </div>
                <div className="tooltipWrapper">
                  <div className="tooltipStyle" style={displayOnHover}>
                    <span>There was an error getting alerts.</span>
                  </div>
                </div>
              </div>
            }
          </div>
        )
    }
}