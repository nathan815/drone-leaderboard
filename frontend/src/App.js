import React from 'react';
import './App.css';
import data from "./data.js"
import dataL from "./dataL.js"
import Checkbox from "./Checkbox.js"


class App extends React.Component {
    componentWillMount = () => {
        this.selectedCheckboxes = new Set();
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

    createCheckboxes = (items) => (
        items.map(this.createCheckbox)
    );

    render() {
        const data1 = data.slice(0, 3);
        const data2 = data.slice(3);
        return (
            <div className="App">
                <header className="App-header">
                    <h1>Rankings</h1>
                    <table className="App-table">
                        <tr>
                            <th> Rank</th>
                            <th> Name</th>
                            <th> Flight Time</th>
                            <th> Group</th>
                            <th> Org</th>
                            <th> Major</th>
                            <th> Flight ID</th>
                        </tr>
                        {data1.map(i => <tr>
                            <td> {i.rank} </td>
                            <td> {i.name} </td>
                            <td> {i.fTime} </td>
                            <td> {i.group} </td>
                            <td> {i.org} </td>
                            <td> {i.major} </td>
                            <td> {i.flight_id} </td>
                        </tr>)}
                        <tr className="App-ignore">
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                        {data2.map(i => <tr>
                            <td> {i.rank} </td>
                            <td> {i.name} </td>
                            <td> {i.fTime} </td>
                            <td> {i.group} </td>
                            <td> {i.org} </td>
                            <td> {i.major} </td>
                            <td> {i.flight_id} </td>
                        </tr>)}
                    </table>
                    <br></br>
                    <h3> Filters </h3>
                    <div class="row">
                        <div class="column">
                            <h4> Groups </h4>
                            <form>
                                {this.createCheckboxes(dataL.groups)}
                            </form>
                        </div>
                        <div class="column">
                            <h4> Majors </h4>
                            <form>
                                {this.createCheckboxes(dataL.majors)}
                            </form>
                        </div>
                        <div class="column">
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
