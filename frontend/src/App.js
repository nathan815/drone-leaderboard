import React from 'react';
import './App.css';
import Checkbox from "./Checkbox.js"

const API_BASE_URL = 'http://localhost:3001';
const BLANK_FILTER_VALUE = 'none';
const BLANK_FILTER_LABEL = '(empty)';

function millisecondsToMinutesSeconds(ms) {
    let totalSeconds = ms / 1000;
    const min = Math.round(totalSeconds / 60);
    const sec = Math.abs(Math.round(totalSeconds % 60));
    return `${min}m ${sec}s`;
}

function filtersQueryStringToObject(queryStr) {
    if(!queryStr) return {};
    const parts = queryStr.split('&');
    const filters = {};
    for(const part of parts) {
        const filterParts = part.split('=');
        filters[filterParts[0]] = filterParts[1] ? filterParts[1].split(',').map(val => decodeURI(val)) : [];
    }
    return filters;
}

function startingFilterState() {
    const filters = filtersQueryStringToObject(window.location.href.split('?')[1]);
    return {
        groups: new Set(filters.groups),
        majors: new Set(filters.majors),
        orgs: new Set(filters.orgs),
    };
}

class App extends React.Component {

    state = {
        leaderboardData: [],
        filterPossibleValues: {},
        showFilters: false,
        filters: startingFilterState(),
        error: null,
        filterError: null
    };

    componentDidMount = () => {
        this.fetchLeaderboardData();
        this.fetchLeaderboardFilters();
        this.interval = setInterval(() => this.fetchLeaderboardData(), 5000);
    };

    componentWillUnmount() {
        clearInterval(this.interval);
    };

    getFiltersQueryString() {
        const filters = this.state.filters;
        const groups = [...filters.groups].join(',');
        const majors = [...filters.majors].join(',');
        const orgs = [...filters.orgs].join(',');
        const parts = { groups, majors, orgs };
        return Object.keys(parts)
            .filter(key => parts[key].length > 0)
            .map(key => key + '=' + parts[key])
            .join('&');
    }

    fetchLeaderboardData = () => {
        const queryString = this.getFiltersQueryString();

        fetch(`${API_BASE_URL}/leaderboard?${queryString}`)
            .then(response => response.json())
            .then((rows) => {
                this.setState({
                    error: null,
                    leaderboardData: rows
                })
            })
            .catch((error) => {
                this.setState({error: 'Error: Unable to fetch leaderboard!'});
                console.log('leaderboard fetch error', error);
            });
    };

    fetchLeaderboardFilters = () => {
        fetch(`${API_BASE_URL}/filter_values`)
            .then(response => response.json())
            .then(filterTypeValues => {
                this.setState({
                    filterError: null,
                    filterPossibleValues: filterTypeValues
                });
            })
            .catch((error) => {
                this.setState({filterError: 'Error: Unable to fetch filters'});
                console.log('filter fetch error', error);
            });
    };

    toggleFilters = (e) => {
        e.preventDefault();
        e.nativeEvent.preventDefault();
        this.setState(state => {
            return {
                showFilters: !state.showFilters
            }
        });
        this.fetchLeaderboardFilters();
    };

    setFilterValue = (filterName, value, isChecked) => {
        this.setState(state => {
            const newFilterSet = new Set(state.filters[filterName]);
            if (isChecked) {
                newFilterSet.add(value);
            } else {
                newFilterSet.delete(value);
            }
            return {
                filters: {
                    ...state.filters,
                    [filterName]: newFilterSet
                }
            };
        }, () => {
            this.fetchLeaderboardData();
            const str = this.getFiltersQueryString();
            window.history.replaceState({}, document.title, '/' + (str && '?' + str));
        });
    };

    createCheckbox = (filterName, value) => {
        const isChecked = this.state.filters[filterName].has(value);
        const label = value === BLANK_FILTER_VALUE ? BLANK_FILTER_LABEL : value;
        return (
            <Checkbox
                value={value}
                label={label}
                isChecked={isChecked}
                onToggle={(newChecked) => this.setFilterValue(filterName, value, newChecked)}
                key={value}
            />
        );
    };

    renderRows = (data) => {
        return data.map(flight => <tr key={flight.id}>
            <td> {flight.rank} </td>
            <td> {flight.pilot.name} </td>
            <td> {millisecondsToMinutesSeconds(flight.duration_ms)} </td>
            <td> {flight.pilot.group || '-'} </td>
            <td> {flight.pilot.org || '-'} </td>
            <td> {flight.pilot.major || '-'} </td>
            {/*<td><small>{flight.id}</small></td>*/}
        </tr>);
    };

    createCheckboxes = (items, filter) => (
        items && items.map((label) => this.createCheckbox(filter, label))
    );

    render() {
        const {filterError, leaderboardData} = this.state;

        const firstThreeRows = leaderboardData.slice(0, 3);
        const restOfRows = leaderboardData.slice(3);

        return (
            <div className="App">
                <div className="App-content">
                    <h1>Rankings</h1>
                    <table className="App-table">
                        <tbody>
                        <tr>
                            <th>#</th>
                            <th>Name</th>
                            <th>Time</th>
                            <th>Group</th>
                            <th>Organization</th>
                            <th>Major</th>
                            {/*<th>Flight ID</th>*/}
                        </tr>
                        {this.renderRows(firstThreeRows)}
                        <tr className="App-ignore">
                            <td colSpan="6"></td>
                        </tr>
                        {this.renderRows(restOfRows)}
                        </tbody>
                    </table>
                    <br/>
                    <br/>
                </div>

                <button className="App-show-filters-btn" onClick={this.toggleFilters}>Filters</button>

                <div className={`App-filters ${this.state.showFilters && 'visible'}`}>
                    <h1>
                        Filters
                        <span onClick={this.toggleFilters} className="App-filters-close">&times;</span>
                    </h1>
                    {filterError && <p>{filterError}</p>}
                    <div className="App-filters-sections">
                        <section>
                            <h2>Group</h2>
                            {this.createCheckboxes(this.state.filterPossibleValues.groups, "groups")}
                        </section>
                        <section>
                            <h2>Major</h2>
                            {this.createCheckboxes(this.state.filterPossibleValues.majors, "majors")}
                        </section>
                        <section>
                            <h2>Organization</h2>
                            {this.createCheckboxes(this.state.filterPossibleValues.orgs, "orgs")}
                        </section>
                    </div>
                </div>

                {this.state.error && <div className="App-error-box">
                    {this.state.error}
                </div>}

            </div>
        );
    }
}

export default App;
