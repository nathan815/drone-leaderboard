import React, {Component} from 'react';

class Checkbox extends Component {
    render() {
        const {label, value, isChecked} = this.props;

        return (
            <div className="checkbox">
                <label>
                    <input
                        type="checkbox"
                        value={value || label}
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
