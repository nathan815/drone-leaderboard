import React from 'react';
import './App.css';
import dataL from "./dataL.js"
import Checkbox from "./Checkbox.js"

const API_BASE_URL = 'http://localhost:3001';

class App extends React.Component {
    state = {leaderboardData: []}

    componentDidMount = () => {
        this.fetchLeaderboardData();
        this.selectedCheckboxes = new Set();
        this.interval = setInterval(() => this.fetchLeaderboardData(), 2500);
    };

    componentWillUnmount() {
        clearInterval(this.interval);
    };

    fetchLeaderboardData = () => {
        fetch(`${API_BASE_URL}/leaderboard`)
            .then(response => response.json())
            .then((rows) => {
                this.setState({
                    leaderboardData: rows
                })
            })
            .catch((error) => {

            })
    };

    toggleCheckbox = label => {
        if (this.selectedCheckboxes.has(label)) {
            this.selectedCheckboxes.delete(label);
        } else {
            this.selectedCheckboxes.add(label);
        }
    };

    handleFormSubmit = formSubmitEvent => {
        formSubmitEvent.preventDefault();

        for (const checkbox of this.selectedCheckboxes) {
            console.log(checkbox, 'is selected.');
        }
    };

    createCheckbox = label => {
        if (label === "") {
            label = "N/A";
        }
        return (<Checkbox
            label={label}
            handleCheckboxChange={this.toggleCheckbox}
            key={label}
        />)
    };

    renderRows = (data) => {
        return data.map(flight => <tr key={flight.id}>
            <td> {flight.rank} </td>
            <td> {flight.pilot.name} </td>
            <td> {flight.duration_ms} </td>
            <td> {flight.group} </td>
            <td> {flight.pilot.org} </td>
            <td> {flight.pilot.major} </td>
            <td> {flight.id} </td>
        </tr>);
    };

    createCheckboxes = (items) => (
        items.map(this.createCheckbox)
    );

    render() {
        const data1 = this.state.leaderboardData.slice(0, 3);
        const data2 = this.state.leaderboardData.slice(3);
        return (
            <div className="App">
                <header className="App-header">
                    <h1>Rankings</h1>
                    <table className="App-table">
                        <tbody>
                        <tr>
                            <th> Rank</th>
                            <th> Name</th>
                            <th> Flight Time</th>
                            <th> Group</th>
                            <th> Org</th>
                            <th> Major</th>
                            <th> Flight ID</th>
                        </tr>
                        {this.renderRows(data1)}
                        <tr className="App-ignore">
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                        {this.renderRows(data2)}
                        </tbody>
                    </table>
                    <br></br>
                    <h3> Filters </h3>
                    <div className="row">
                        <div className="column">
                            <h4> Groups </h4>
                            <form>
                                {this.createCheckboxes(dataL.groups)}
                            </form>
                        </div>
                        <div className="column">
                            <h4> Majors </h4>
                            <form>
                                {this.createCheckboxes(dataL.majors)}
                            </form>
                        </div>
                        <div className="column">
                            <h4> Organizations </h4>
                            <form>
                                {this.createCheckboxes(dataL.organizations)}
                            </form>
                        </div>
                    </div>
                </header>

            </div>
        );
    }
}

export default App;
