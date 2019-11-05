import React, {Component} from 'react';

class Checkbox extends Component {
    state = {
        isChecked: false,
    }

    render() {
        const {label, isChecked} = this.props;

        return (
            <div className="checkbox">
                <label>
                    <input
                        type="checkbox"
                        value={label}
                        checked={isChecked}
                        onChange={() => this.props.onToggle(!isChecked)}
                    />

                    {label}
                </label>
            </div>
        );
    }
}


export default Checkbox;