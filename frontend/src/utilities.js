/* Takes end and start as seconds and converts duration to HH:mm:ss format */

import moment from "moment";

export const durationString = ({end, start}) => {
    const milliseconds = 1000 * (end - start)
    const duration = moment.duration(milliseconds);
    return moment.utc(duration.asMilliseconds()).format('HH:mm:ss')
}