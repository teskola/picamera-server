import { Button, Dialog, DialogActions, DialogTitle } from "@mui/material";
import { Fragment, useEffect, useState } from "react";

const DeleteDialog = (props) => {

    useEffect(() => {
        setOpen(props.open)

      }, [props.open]);

    const [open, setOpen] = useState(props.open)   

    return (
        <Fragment>          
          <Dialog
            open={open}
            onClose={props.onCancel}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
          >
            <DialogTitle id="alert-dialog-title">
              {"Are you sure you want to delete recording?"}
            </DialogTitle>            
            <DialogActions>
              <Button onClick={props.onCancel}>Cancel</Button>
              <Button onClick={props.onConfirm} autoFocus>
                Delete
              </Button>
            </DialogActions>
          </Dialog>
        </Fragment>
      );
}

export default DeleteDialog