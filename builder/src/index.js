import React, { Fragment, useEffect, useState } from "react";
import { render } from "react-dom";
import Draggable from "react-draggable";

import "./index.css";

const props = {
    before_start_x: 0,
    before_start_y: 0,
    before_end_x: 0,
    before_end_y: 0,
    after_start_x: 0,
    after_start_y: 0,
    after_end_x: 0,
    after_end_y: 0,
};

const draggers = Object.keys(props)
    .map((k) => k.replace(/_[xy]/g, ""))
    .filter((e, i, a) => !a.slice(0, i).includes(e));

const letters = "bcdfgjklmnpqrstvwxyz".split("");

const initDelta = (ls, ps) => {
    let out = {};

    for (let l of ls) {
        out[l] = { ...ps };
    }

    return out;
};

const Button = ({ content, callback, value }) => {
    const cls = content === value ? "active" : "";
    return (
        <button onClick={(e) => callback(content)} className={cls}>
            {content}
        </button>
    );
};

const Builder = () => {
    const [letter, setLetter] = useState("b");
    const [angle, setAngle] = useState(4);
    const [angleEl, setAngleEl] = useState({ x: 0, y: 0 });
    const [delta, setDelta] = useState(initDelta(letters, props));
    const [pps, setPps] = useState(props);

    const [output, setOutput] = useState("");

    useEffect(() => {
        const headers = [
            "base",
            "before_start_x",
            "before_start_y",
            "before_end_x",
            "before_end_y",
            "after_start_x",
            "after_start_y",
            "after_end_x",
            "after_end_y",
        ];
        let output = [headers];
        let blank = [];

        for (let l of letters) {
            let temp = [l];

            for (let v in delta[l]) {
                temp.push(delta[l][v] % 210);
            }

            output.push(temp.join(","));

            if (l === "w") {
                temp[0] = "blank";
                blank = temp.join(",");
            }
        }

        if (blank.length) {
            output.push(blank);
        }

        setOutput(output.join("\n"));
    }, [delta]);

    useEffect(() => {
        const poss = [
            { x: 0, y: 210 },
            { x: 0, y: 420 },
            { x: 210, y: 210 },
            { x: 210, y: 0 },
            { x: 0, y: 0 },
        ][angle];
        setAngleEl(poss);
    }, [angle]);

    useEffect(() => {
        setPps(delta[letter]);
    }, [letter, delta]);

    const dragHandler = (e, d) => {
        let updated = { ...delta };
        const id = d.node.id;

        updated[letter] = pps;
        updated[letter][id + "_x"] = d.x;
        updated[letter][id + "_y"] = d.y;

        setDelta(updated);
    };

    const draggerProps = {
        bounds: "section",
        onStop: dragHandler,
        grid: [5, 5],
    };

    return (
        <Fragment>
            <section style={{ background: `url(./img/${letter}.png)` }}>
                {draggers.map((d) => (
                    <Draggable key={d} {...draggerProps}>
                        <div id={d} className="pointer" />
                    </Draggable>
                ))}
                <Draggable position={angleEl} disabled={true}>
                    <div className="angle" />
                </Draggable>
            </section>

            {Array(5)
                .fill()
                .map((_, i) => (
                    <Button
                        key={"ang-" + i}
                        content={parseInt(i)}
                        callback={setAngle}
                        value={angle}
                    />
                ))}

            {letters.map((l, i) => (
                <Button
                    key={"ltr-" + i}
                    content={l}
                    callback={setLetter}
                    value={letter}
                />
            ))}

            {draggers.map((d) => (
                <div id={d} key={d} className="label">
                    {d}
                </div>
            ))}

            <textarea id="output" defaultValue={output} />
        </Fragment>
    );
};

render(<Builder />, document.getElementById("root"));
