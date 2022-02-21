import React, {Component}  from 'react';

class AddNewTest extends Component {
  render(){
    return (
        <div className="row">
            <div className="col-md-12">
              <fieldset>
                <legend>New Test</legend>
                <form>
                  <div className="row">
                    <div className="col-md-10 form-group">
                      <input type="file"
                        className="form-control-file"
                        data-testid='newTestFile'
                        name="newTestFile"
                        id="newTestFile"
                        accept='.py'
                        ref={this.props.fileInput}
                      />
                      <p className="error-message">{this.props.newTestFileError}</p>
                    </div>
                    <div className="col-md-2">
                      {
                        this.props.status === 'uploading' &&  <div class="spinner-border text-primary" role="status"> <span class="sr-only">Loading...</span></div>
                      }
                      {
                        this.props.status === 'idle' &&  <input data-testid='submitButton' type="button" className="btn btn-primary" value="Submit" onClick={this.props.uploadTestFile}/>
                      }
                      
                    </div>
                  </div>
                </form>
              </fieldset>
            </div>
          </div>
    );
  }
}

export default AddNewTest;